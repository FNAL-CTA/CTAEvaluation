#! /usr/bin/env python3

import binascii
import csv
import json
import os
import pdb
import subprocess
import time
from typing import Tuple
from zlib import adler32

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

import cta_common_pb2
from CTADatabaseModel import ArchiveFile, TapeFile
from FileWrappers import VOL1, HDR1, HDR2, EOF1, EOF2, UHL1, UTL1
from TapeAccess import load_tape, copy_file_to_tape, make_tape_mark, write_data_to_tape

CTA_INSTANCE = 'ctaeos5'
DEVICE = '/dev/nst1'
DEVICE_NUM = 0
LIBRARY_NUM = 5
VID_VALUE = 'V01005'
EPOCH_031 = '020001'

MIGRATION_CONF = '/CTAEvaluation/replacements/migration.conf'
FILES_TO_READ = ['/etc/group']
BLOCKSIZE = 256 * 1024 * 1024


class EosInfo:
    def __init__(self, server: str):
        self.eos_ids = {}
        self.server = server

    def id_for_file(self, path: str) -> int:
        """
        Cache and retrieve the IDs of a path

        :param path: The full path of the file or directory to get the ID for
        :return: the ID number of the path
        """
        if path in self.eos_ids:
            return self.eos_ids[path]
        eos_url = f"root://{self.server}"
        result = subprocess.run(['eos', '--json', eos_url, 'info', path], stdout=subprocess.PIPE)
        eos_info = json.loads(result.stdout.decode('utf-8'))
        try:
            self.eos_ids[path] = eos_info['id']
        except KeyError:
            return None
        return self.eos_ids[path]


class MigrationConfig:
    def __init__(self, file_name):
        self.values = {}
        with open(file_name) as handle:
            for line in handle:
                if not (line.lstrip().startswith('#') or line.isspace()):
                    key, value = line.split()[:2]
                    self.values[key] = value


def adler_checksum(file_name: str) -> Tuple[int, str]:
    adler_sum = 1
    with open(file_name, "rb") as file_handle:
        # FIXME: Use Walrus operator for python 3.8 (while data := file_handle.read and no break)
        while True:
            data = file_handle.read(BLOCKSIZE)
            if not data:
                break
            adler_sum = adler32(data, adler_sum)
    return adler_sum, hex(adler_sum)[2:10].zfill(8).lower()


def get_checksum_blob(adler32: str) -> str:
    """
    Generate a Google protobuf representation of the checksum(s) and type(s)

    :param adler32: 8-character string for 32-bit ADLER32 checksum
    :return: Blob as StringSerialized, ready to insert into database
    """
    csb = cta_common_pb2.ChecksumBlob()

    my_cs = csb.cs.add()
    my_cs.type = my_cs.ADLER32
    adler32_r = adler32[6:8] + adler32[4:6] + adler32[2:4] + adler32[0:2]
    my_cs.value = bytes.fromhex(adler32_r)

    return csb.SerializeToString()


def main():
    config = MigrationConfig(MIGRATION_CONF)
    eos_server = config.values['eos.endpoint'].split(':')[0]  # Just hostname. The port is probably gRPC
    cta_prefix = config.values['eos.prefix']
    eos_info = EosInfo(eos_server)

    engine = create_engine('postgresql://cta:cta@postgres/cta', echo=True)

    # Build the list of files for EOS to insert
    with open('/tmp/eos_files.csv', 'w') as csvfile:
        eos_file_inserts = csv.writer(csvfile, lineterminator='\n')
        for file_name in FILES_TO_READ:
            uid = 1000
            gid = 1000
            enstore_id = 0
            file_size = os.path.getsize(file_name)
            adler_int, adler_string = adler_checksum(file_name)
            ctime = mtime = int(time.time())

            # Get the EOS container ID and set all paths correctly
            destination_file = os.path.normpath(cta_prefix + '/' + file_name)
            eos_directory, base_file = os.path.split(destination_file)
            short_directory, base_file = os.path.split(file_name)
            container_id = eos_info.id_for_file(eos_directory)

            eos_file_inserts.writerow([enstore_id, container_id, uid, gid, file_size, adler_string,
                                       ctime, mtime, short_directory, base_file])

    # Actually insert the files
    result = subprocess.run(['/root/eos-import-files-csv', '-c', MIGRATION_CONF], stdout=subprocess.PIPE)

    with Session(engine) as session:
        for file_name in FILES_TO_READ:
            # FIXME: Probably should store these
            file_size = os.path.getsize(file_name)
            adler_int, adler_string = adler_checksum(file_name)
            adler_blob = get_checksum_blob(adler_string)

            eos_file = os.path.normpath(cta_prefix + '/' + file_name)
            print(f"Checking EOS ID for {eos_file}")
            eos_id = eos_info.id_for_file(eos_file)
            print(f"EOS ID is {eos_id}")
            print(f"Checksum is {adler_string}")
            archive_file = ArchiveFile(disk_instance_name=CTA_INSTANCE, disk_file_id=eos_id, disk_file_uid=1000,
                                       disk_file_gid=1000, size_in_bytes=file_size, checksum_blob=adler_blob,
                                       checksum_adler32=adler_int, storage_class_id=1, creation_time=int(time.time()),
                                       reconciliation_time=int(time.time()), is_deleted='0')
            session.add(archive_file)
            session.flush()
            print(f"File inserted is {archive_file.archive_file_id}")

            try:
                next_fseq = session.scalar(select(TapeFile.fseq).filter_by(vid=VID_VALUE)
                                           .order_by(TapeFile.fseq.desc()).limit(1)) + 1
            except TypeError:
                next_fseq = 1

            print(f"Next spot on tape is {next_fseq}")

            tape_file = TapeFile(vid=VID_VALUE, fseq=next_fseq, block_id=0, logical_size_in_bytes=file_size,
                                 copy_nb=1, creation_time=int(time.time()),
                                 archive_file_id=archive_file.archive_file_id)
            session.add(tape_file)

        session.commit()

    # Write a tape
    if True:
        load_tape(tape=LIBRARY_NUM, drive=DEVICE_NUM)

        vol1 = VOL1(volume_id=VID_VALUE)
        write_data_to_tape(device=DEVICE, data=vol1.data())

        hdr1 = HDR1(file_id=1, file_set_id=VID_VALUE, file_section_number=1, file_seq_number=1, gen_number=1,
                    gen_ver_number=0, creation_date=EPOCH_031, expiration_date=EPOCH_031, file_access=' ',
                    block_count=0,
                    implementation_id='CASTOR 2.1.15')
        write_data_to_tape(device=DEVICE, data=hdr1.data())

        hdr2 = HDR2(record_format='F', block_length=0, record_length=0, implementation_id='P', offset_length=0)
        write_data_to_tape(device=DEVICE, data=hdr2.data())

        uhl1 = UHL1(file_seq_number=1, block_length=256 * 1024, record_length=256 * 1024, site='CTA',
                    hostname='TPSRV01', drive_mfg='STK', drive_model='MHVTL', drive_serial_num='VDSTK11')
        write_data_to_tape(device=DEVICE, data=uhl1.data())

        make_tape_mark(device=DEVICE)
        copy_file_to_tape(device=DEVICE, file_name=FILES_TO_READ[0] )
        make_tape_mark(device=DEVICE)

        eof1 = EOF1(file_id=1, file_set_id=VID_VALUE, file_section_number=1, file_seq_number=1, gen_number=1,
                    gen_ver_number=0, creation_date=EPOCH_031, expiration_date=EPOCH_031, file_access=' ',
                    block_count=1,
                    implementation_id='CASTOR 2.1.15')
        write_data_to_tape(device=DEVICE, data=eof1.data())

        eof2 = EOF2(record_format='F', block_length=0, record_length=0, implementation_id='P', offset_length=0)
        write_data_to_tape(device=DEVICE, data=eof2.data())


        utl1 = UTL1(file_seq_number=1, block_length=256 * 1024, record_length=256 * 1024, site='CTA',
                    hostname='TPSRV01',
                    drive_mfg='STK', drive_model='MHVTL', drive_serial_num='VDSTK11')
        write_data_to_tape(device=DEVICE, data=utl1.data())

        make_tape_mark(device=DEVICE)

main()
