#! /usr/bin/env python3

import csv
import os
import subprocess
import time
from typing import Tuple, List
from zlib import adler32

from sqlalchemy import create_engine, update, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import cta_common_pb2
from CTADatabaseModel import ArchiveFile, TapeFile, Tape
from EosInfo import EosInfo
from MigrationConfig import MigrationConfig

FORCE_OLD_ADLER32 = True

CTA_INSTANCE = 'ctaeos'
VID_VALUE = 'VR5775'

MIGRATION_CONF = '/CTAEvaluation/replacements/migration.conf'

SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.environ.get('SQL_PASSWORD')
SQL_HOST = os.getenv('SQL_HOST')


# def adler_checksum(file_name: str) -> Tuple[int, str]:
#     adler_sum = 1
#     with open(file_name, "rb") as file_handle:
#         # FIXME: Use Walrus operator for python 3.8 (while data := file_handle.read and no break)
#         while True:
#             data = file_handle.read(BLOCKSIZE)
#             if not data:
#                 break
#             adler_sum = adler32(data, adler_sum)
#     return adler_sum, hex(adler_sum)[2:10].zfill(8).lower()


def convert_0_adler32_to_1_adler32(crc: int, filesize: int) -> Tuple[int, str]:
    """
    Dmitry:
    OK, I did some archaelogy.
    the switchover to seed 1 occured on 2019-08-21 09:54:26.
    It was a downtime day. So all files wih update datestamp < 2019-08-21 09:54:26 have crc seeded 0,
    Anything newer - seed 1 (no new data was written until 11 AM on that day).
    """

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

    engine = create_engine(f'postgresql://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}/cta', echo=True)

    # Read in the list of of files to migrate
    enstore_files = []
    with open(f'../data/{VID_VALUE}M8.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            enstore_files.append(row)

    # Make Enstore directories for the files
    eos_files = [row['pnfs_path'] for row in enstore_files]
    make_eos_subdirs(eos_prefix=cta_prefix, eos_files=eos_files)

    # Create a new Enstore tape in DB or modify the tape to have Enstore format
    try:
        with Session(engine) as session:
            tape = create_m8_tape(vid=VID_VALUE, drive='VDSTK11')
            session.add(tape)
            session.commit()
    except IntegrityError:
        with Session(engine) as session:
            stmt = (update(Tape)
                    .where(Tape.vid == VID_VALUE)
                    .values(label_format=2)  # FIXME: This is not setting the tape to M8 yet
                    .execution_options(synchronize_session="fetch"))
            result = session.execute(stmt)
            session.commit()

    file_ids = {}

    with Session(engine) as session:
        # FIXME: Use the actual largest number plus some as the start value
        # from sqlalchemy.sql.expression import func (or just from sqlalchemy)
        # stmt = select(func.max(ArchiveFile.disk_file_id))
        # result = session.execute(stmt) .scalar() perhaps

        for eos_id, enstore_file in enumerate(enstore_files, start=1000000):
            file_name = enstore_file['pnfs_path']
            file_size = int(enstore_file['size'])
            if FORCE_OLD_ADLER32:  # FIXME: Based on date, see function
                adler_int, adler_string = convert_0_adler32_to_1_adler32(int(enstore_file['crc']), file_size)
            else:
                raise NotImplementedError('Need a function to just convert int to string')
            adler_blob = get_checksum_blob(adler_string)

            eos_file = os.path.normpath(cta_prefix + '/' + file_name)
            # FIXME: Try catch here to continue on if the file is already inserted
            print(f"Checksum is {adler_string}")
            archive_file = ArchiveFile(disk_instance_name=CTA_INSTANCE, disk_file_id=eos_id, disk_file_uid=1000,
                                       disk_file_gid=1000, size_in_bytes=file_size, checksum_blob=adler_blob,
                                       checksum_adler32=adler_int, storage_class_id=1, creation_time=int(time.time()),
                                       reconciliation_time=int(time.time()), is_deleted='0')
            session.add(archive_file)
            session.flush()
            print(f"File inserted is {archive_file.archive_file_id}")
            file_ids[file_name] = archive_file.archive_file_id
            enstore_fseq = int(enstore_file['location_cookie'].split('_')[2])  # pull off last field and make integer

            print(f"Putting this file at FSEQ {enstore_fseq}")

            tape_file = TapeFile(vid=VID_VALUE, fseq=enstore_fseq, block_id=enstore_fseq,
                                 logical_size_in_bytes=file_size,
                                 copy_nb=1, creation_time=int(time.time()),
                                 archive_file_id=archive_file.archive_file_id)
            session.add(tape_file)

        session.commit()

    # Build the list of files for EOS to insert
    with open('/tmp/eos_files.csv', 'w') as csvfile:
        eos_file_inserts = csv.writer(csvfile, lineterminator='\n')
        for enstore_file in enstore_files:
            file_name = enstore_file['pnfs_path']
            uid = 1000
            gid = 1000
            enstore_id = enstore_file['bfid']
            file_size = int(enstore_file['size'])
            if FORCE_OLD_ADLER32:
                adler_int, adler_string = convert_0_adler32_to_1_adler32(int(enstore_file['crc']), file_size)
            else:
                raise NotImplementedError('Need a function to just convert int to string')
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
        for enstore_file in enstore_files:
            file_name = enstore_file['pnfs_path']
            eos_file = os.path.normpath(cta_prefix + '/' + file_name)
            print(f"Checking EOS ID for {eos_file}")
            eos_id = eos_info.id_for_file(eos_file)  # FIXME: Check that eos_id is not null and skip if it is
            archive_file_id = file_ids[file_name]
            stmt = (update(ArchiveFile)
                    .where(ArchiveFile.archive_file_id == archive_file_id)
                    .values(disk_file_id=eos_id)
                    .execution_options(synchronize_session="fetch"))

            result = session.execute(stmt)
        session.commit()


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


def create_m8_tape(vid, drive):
    tape = Tape(vid=vid, media_type_id=5,
                vendor='TBD',
                logical_library_id=1,
                tape_pool_id=1,
                encryption_key_name='',
                data_in_bytes=0,
                last_fseq=0,
                nb_master_files=0,  # FIXME?
                master_data_in_bytes=0,  # FIXME?
                is_full='0',  # FIXME: Set to full when migrated
                is_from_castor='0',
                dirty='0',
                nb_copy_nb_1=0,
                copy_nb_1_in_bytes=0,
                nb_copy_nb_gt_1=0,
                copy_nb_gt_1_in_bytes=0,
                label_format=2,
                label_drive=drive,
                label_time=int(time.time()),  # Volume.first_access?
                last_read_drive=drive,
                last_read_time=int(time.time()),  # Volume.last_access?
                last_write_drive=drive,
                last_write_time=int(time.time()),
                read_mount_count=0,  # Volume.sum_mounts?
                write_mount_count=0,  # volume.sum_mounts?
                user_comment='Migrated from Enstore',
                tape_state='ACTIVE',  # ACTIVE/DISABLED/BROKEN/REPACKING
                state_reason='Migrated from Enstore',
                state_update_time=int(time.time()),
                state_modified_by='ewv',
                creation_log_user_name='ewv',
                creation_log_host_name='enstore.fnal.gov',
                creation_log_time=int(time.time()),
                last_update_user_name='ewv',
                last_update_host_name='enstore.fnal.gov',
                last_update_time=int(time.time()),
                verification_status='',
                )

    return tape


def update_counts():
    """ FIXME: Update the tape byte counts on every insert"""
    pass
    """
    something like....
    session = Session()
    u = session.query(User).get(123)
    u.name = u"Bob Marley"
    session.commit()"""


main()
