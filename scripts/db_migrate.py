#! /usr/bin/env python3

import csv
import os
import subprocess
import time
from typing import Tuple, List
from zlib import adler32

from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

import cta_common_pb2
from CTADatabaseModel import ArchiveFile, TapeFile, Tape
from EosInfo import EosInfo
from FileWrappers import VOL1, HDR1, HDR2, EOF1, EOF2, UHL1, UTL1, EnstoreVOL1
from MigrationConfig import MigrationConfig
from TapeAccess import Drive, Changer

CTA_INSTANCE = 'ctaeos'
DEVICE = '/dev/nst1'
CHANGER_DEVICE = '/dev/smc'
DEVICE_NUM = 0
LIBRARY_NUM = 5
VID_VALUE = 'V01005'
EPOCH_031 = '020001'

MIGRATION_CONF = '/CTAEvaluation/replacements/migration.conf'
FILES_TO_READ = ['/etc/group', '/etc/services', '/etc/nanorc']
BLOCKSIZE = 256 * 1024 * 1024


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


def convert_0_adler32_to_1_adler32(crc: int, filesize: int) -> Tuple[int, str]:
    BASE = 65521

    size = filesize % BASE
    s1 = (crc & 0xffff)
    s2 = ((crc >> 16) & 0xffff)
    s1 = (s1 + 1) % BASE
    s2 = (size + s2) % BASE
    new_adler = (s2 << 16) + s1
    return new_adler, hex(new_adler)[2:10].zfill(8).lower()


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

    # Update the tape to be Enstore
    with Session(engine) as session:
        stmt = (update(Tape)
                .where(Tape.vid == VID_VALUE)
                # .values(label_format=b'\x02'.decode('utf-8'))
                .values(label_format=2)
                .execution_options(synchronize_session="fetch"))

        result = session.execute(stmt)
        session.commit()

    make_eos_subdirs(eos_prefix=cta_prefix, eos_files=FILES_TO_READ)

    file_ids = {}

    with Session(engine) as session:
        eos_id = 999999
        for file_name in FILES_TO_READ:
            # FIXME: Probably should store these
            file_size = os.path.getsize(file_name)
            adler_int, adler_string = adler_checksum(file_name)
            adler_blob = get_checksum_blob(adler_string)

            eos_file = os.path.normpath(cta_prefix + '/' + file_name)
            print(f"Checking EOS ID for {eos_file}")
            eos_id += 1
            print(f"EOS ID is {eos_id}")
            print(f"Checksum is {adler_string}")
            archive_file = ArchiveFile(disk_instance_name=CTA_INSTANCE, disk_file_id=eos_id, disk_file_uid=1000,
                                       disk_file_gid=1000, size_in_bytes=file_size, checksum_blob=adler_blob,
                                       checksum_adler32=adler_int, storage_class_id=1, creation_time=int(time.time()),
                                       reconciliation_time=int(time.time()), is_deleted='0')
            session.add(archive_file)
            session.flush()
            print(f"File inserted is {archive_file.archive_file_id}")
            file_ids[file_name] = archive_file.archive_file_id
            try:
                next_fseq = session.scalar(select(TapeFile.fseq).filter_by(vid=VID_VALUE)
                                           .order_by(TapeFile.fseq.desc()).limit(1)) + 1
            except TypeError:
                next_fseq = 1

            print(f"Next spot on tape is {next_fseq}")

            tape_file = TapeFile(vid=VID_VALUE, fseq=next_fseq, block_id=next_fseq, logical_size_in_bytes=file_size,
                                 copy_nb=1, creation_time=int(time.time()),
                                 archive_file_id=archive_file.archive_file_id)
            session.add(tape_file)

        session.commit()

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
            archive_file_id = file_ids[file_name]

            eos_file_inserts.writerow([enstore_id, container_id, uid, gid, file_size, adler_string,
                                       ctime, mtime, short_directory, base_file, archive_file_id])
    # Actually insert the files into EOS
    result = subprocess.run(['/root/eos-import-files-csv', '-c', MIGRATION_CONF], stdout=subprocess.PIPE)

    # Update the EOS ID for the files just inserted
    with Session(engine) as session:
        for file_name in FILES_TO_READ:
            # FIXME: Probably should store these

            eos_file = os.path.normpath(cta_prefix + '/' + file_name)
            print(f"Checking EOS ID for {eos_file}")
            eos_id = eos_info.id_for_file(eos_file)
            archive_file_id = file_ids[file_name]
            stmt = (update(ArchiveFile)
                    .where(ArchiveFile.archive_file_id == archive_file_id)
                    .values(disk_file_id=eos_id)
                    .execution_options(synchronize_session="fetch"))

            result = session.execute(stmt)
        session.commit()

    # Write a tape
    if True:
        # write_castor_tape()
        write_enstore_tape()


def write_enstore_tape():
    changer = Changer()
    drive = Drive(device=DEVICE)
    changer.load_tape(tape=LIBRARY_NUM, drive=DEVICE_NUM)
    drive.rewind_tape()
    write_enstore_label(drive=drive, volume_id=VID_VALUE)
    for file_name in FILES_TO_READ:
        drive.copy_file_to_tape_as_cpio(file_name=file_name)
    changer.unload_tape(tape=LIBRARY_NUM, drive=DEVICE_NUM)


def write_castor_tape():
    changer = Changer()
    drive = Drive(device=DEVICE)
    changer.load_tape(tape=LIBRARY_NUM, drive=DEVICE_NUM)
    drive.rewind_tape()
    write_castor_header(drive, VID_VALUE, with_label=True)
    drive.copy_file_to_tape(file_name=FILES_TO_READ[0])
    write_castor_trailer(drive, volume_id=VID_VALUE)
    changer.unload_tape(tape=LIBRARY_NUM, drive=DEVICE_NUM)


def make_eos_subdirs(eos_files: List[str], sleep_time: int = 10, eos_prefix='/'):
    """
    Make the subdirectories for the files we are going to be writing

    :param eos_prefix:
    :param eos_files: List of files
    :param sleep_time: Time to sleep after making directories in EOS
    :return:
    """

    eos_directories = set()
    for eos_file in eos_files:
        eos_directory = os.path.dirname(os.path.normpath(eos_prefix + '/' + eos_file))
        eos_directory = eos_directory.lstrip('/')
        eos_directories.add(eos_directory)

    for eos_directory in eos_directories:
        print(f'Making directory {eos_directory}')
        result = subprocess.run(['eos', 'root://ctaeos', 'mkdir', '-p', eos_directory], stdout=subprocess.PIPE)

    time.sleep(sleep_time)


# FIXME: Move this to the class
def write_castor_header(drive: Drive, volume_id: str, with_label: bool = True):
    header_bytes: bytes = b''
    if with_label:
        vol1 = VOL1(volume_id=VID_VALUE)
        header_bytes += vol1.data()

    hdr1 = HDR1(file_id=1, file_set_id=volume_id, file_section_number=1, file_seq_number=1, gen_number=1,
                gen_ver_number=0, creation_date=EPOCH_031, expiration_date=EPOCH_031, file_access=' ',
                block_count=0,
                implementation_id='CASTOR 2.1.15')

    header_bytes += hdr1.data()

    hdr2 = HDR2(record_format='F', block_length=0, record_length=0, implementation_id='P', offset_length=0)
    header_bytes += hdr2.data()

    uhl1 = UHL1(file_seq_number=1, block_length=256 * 1024, record_length=256 * 1024, site='CTA',
                hostname='TPSRV01', drive_mfg='STK', drive_model='MHVTL', drive_serial_num='VDSTK11')
    header_bytes += uhl1.data()

    drive.write_data_to_tape(data=header_bytes, block_size=80)


def write_enstore_label(drive: Drive, volume_id: str):
    header_bytes: bytes = b''
    vol1 = EnstoreVOL1(volume_id=volume_id)
    header_bytes += vol1.data()

    drive.write_data_to_tape(data=header_bytes, block_size=80)


def write_castor_trailer(drive, volume_id):
    eof1 = EOF1(file_id=1, file_set_id=volume_id, file_section_number=1, file_seq_number=1, gen_number=1,
                gen_ver_number=0, creation_date=EPOCH_031, expiration_date=EPOCH_031, file_access=' ',
                block_count=1,
                implementation_id='CASTOR 2.1.15')
    trailer_bytes = eof1.data()

    # drive.write_data_to_tape(data=eof1.data())
    eof2 = EOF2(record_format='F', block_length=0, record_length=0, implementation_id='P', offset_length=0)
    trailer_bytes += eof2.data()

    # drive.write_data_to_tape(data=eof2.data())
    utl1 = UTL1(file_seq_number=1, block_length=256 * 1024, record_length=256 * 1024, site='CTA',
                hostname='TPSRV01',
                drive_mfg='STK', drive_model='MHVTL', drive_serial_num='VDSTK11')
    trailer_bytes += utl1.data()

    drive.write_data_to_tape(data=trailer_bytes, block_size=80)
    # drive.make_tape_mark()


main()
