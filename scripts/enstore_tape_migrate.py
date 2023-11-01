#! /usr/bin/env python3

import argparse
import csv
import json
import os
import subprocess
import time
import uuid

from sqlalchemy import MetaData, Table, create_engine, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from CTADatabaseModel import ArchiveFile, MediaType, TapeFile, Tape
from CTAUtils import get_adler32_string, get_checksum_blob, add_media_types, make_eos_subdirs
from EnstoreUtils import get_switch_epoch, convert_0_adler32_to_1_adler32, decode_bfid
from MigrationConfig import MigrationConfig

# CTA_INSTANCE = 'ctaeos'
CTA_INSTANCE = 'eosdev'  # FIXME
# VID_VALUE = 'VR1866'

# DCACHE_MIGRATION = True

MIGRATION_CONF = '/CTAEvaluation/replacements/migration.conf'

SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.environ.get('SQL_PASSWORD')
SQL_HOST = os.getenv('SQL_HOST')
SQL_PORT = os.getenv('SQL_PORT')
SQL_DB = os.getenv('SQL_DB')

ENSTORE_USER = os.getenv('ENSTORE_USER')
ENSTORE_PASSWORD = os.environ.get('ENSTORE_PASSWORD')
ENSTORE_HOST = os.getenv('ENSTORE_HOST')
ENSTORE_PORT = os.getenv('ENSTORE_PORT')
ENSTORE_DB = os.getenv('ENSTORE_DB')

EOS_INSERT_LIST = '/tmp/eos-insert-list.json'

# FROM_ENSTORE = True
# FROM_CSV = False

parser = argparse.ArgumentParser(prog='EnstoreMigrate',
                                 description='Migrate a tape from Enstore (either DB or a CSV representation) into CTA',
                                 epilog=None)

parser.add_argument('vid')
parser.add_argument('-s', '--source', choices=['db', 'csv'], required=True,
                    help='The source of the information for a tape. Database or CSV file')
parser.add_argument('-d', '--destination', choices=['eos', 'dcache'], required=True,
                    help='Whether the target file system is EOS or dCache')
parser.add_argument('-v', '--verbose', action='store_true', help='Debug mode. Will print all SQL statements')


def main():

    # Extract command line arguments
    args = parser.parse_args()

    migrate_vid = args.vid

    from_enstore = True
    from_csv = False
    to_dCache = False
    if args.source == 'csv':
        from_enstore = False
        from_csv = True
    if args.destination == 'dcache':
        to_dCache = True

    debug = args.verbose

    # Extract values from migration config file
    config = MigrationConfig(MIGRATION_CONF)
    cta_prefix = config.values['eos.prefix']

    engine = create_engine(f'postgresql://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}', echo=False)

    # Pre-setup
    add_media_types(engine=engine)

    # This is how we read from a file
    if from_csv:
        enstore_files = enstore_files_from_csv(vid=migrate_vid)
        create_cta_tape(engine=engine, vid=migrate_vid)

    if from_enstore:
        enstore_files = []
        # enstore = create_engine(f'postgresql://{ENSTORE_USER}:{ENSTORE_PASSWORD}@{ENSTORE_HOST}/dmsen_enstoredb',
        connect_string = f'postgresql://{ENSTORE_USER}:{ENSTORE_PASSWORD}@{ENSTORE_HOST}:{ENSTORE_PORT}/{ENSTORE_DB}'
        enstore = create_engine(connect_string, echo=debug, future=True)

        metadata_obj = MetaData()
        EnstoreFiles = Table("file", metadata_obj, autoload_with=enstore)
        EnstoreVolumes = Table("volume", metadata_obj, autoload_with=enstore)

        with Session(enstore, future=True) as enstore_session:
            volume = enstore_session.execute(
                select(EnstoreVolumes).where(EnstoreVolumes.c.label == migrate_vid + 'M8')).first()
            for row in enstore_session.execute(select(EnstoreFiles).where(EnstoreFiles.c.volume == volume.id)):
                enstore_files.append(row._mapping)
        create_cta_tape_from_enstore(engine=engine, volume=volume)

    # Make EOS directories for the files
    eos_files = [enstore_file['pnfs_path'] for enstore_file in enstore_files]
    if not to_dCache:
        make_eos_subdirs(eos_prefix=cta_prefix, eos_files=eos_files)

    # Put files in CTA database
    file_ids = insert_cta_files(engine, enstore_files)

    # Make EOS file placeholders for the files
    if not to_dCache:
        create_eos_files(cta_prefix, enstore_files, file_ids)
    return


def create_eos_files(cta_prefix, enstore_files, file_ids):
    """
    Create the files in EOS and link them to CTA files using cta-eos-namespace-inject
    """

    EOS_METHOD = 'XrdSecPROTOCOL=sss'
    EOS_KEYTAB = 'XrdSecSSSKT=/keytabs/ctafrontend_server_sss.keytab'

    files_need_creating = False
    existing_files = existing_eos_files(cta_prefix, enstore_files)

    number_existing = 0
    number_needed = 0

    # Build the list of files for EOS to insert
    with open(EOS_INSERT_LIST, 'w') as jsonfile:
        for enstore_file in enstore_files:
            file_name = enstore_file['pnfs_path']
            enstore_id = enstore_file['bfid']
            enstore_id = enstore_id.replace('GCMS', '01')  # FIXME: EOS wants an integer for the value. Map it.
            file_size = int(enstore_file['size'])
            _dummy, file_timestamp, _dummy = decode_bfid(enstore_file['bfid'])
            if file_timestamp < get_switch_epoch():
                adler_int, adler_string = convert_0_adler32_to_1_adler32(int(enstore_file['crc']), file_size)
            else:
                adler_int, adler_string = get_adler32_string(int(enstore_file['crc']))

            # Get the EOS container ID and set all paths correctly
            destination_file = os.path.normpath(cta_prefix + '/' + file_name)

            archive_file_id = file_ids[file_name]
            if destination_file not in existing_files:
                files_need_creating = True
                number_needed += 1
                new_eos_file = {'eosPath': destination_file, 'diskInstance': CTA_INSTANCE,
                                'archiveId': str(archive_file_id), 'size': str(file_size), 'checksumType': 'ADLER32',
                                'checksumValue': adler_string, 'enstoreId': enstore_id}
                jsonfile.write(json.dumps(new_eos_file) + '\n')
            else:
                number_existing += 1

    print(f'Checking {len(enstore_files)} CTA files: {number_existing} already existed, {number_needed} to be created')

    # Actually insert the files into EOS
    if files_need_creating:
        result = subprocess.run(['env', EOS_METHOD, EOS_KEYTAB, 'cta-eos-namespace-inject', '--json', EOS_INSERT_LIST],
                                stdout=subprocess.PIPE)

        if result.returncode:
            print(f'Problem with insert script:{result}')
        else:
            print('Everything appears to have gone well')


def existing_eos_files(cta_prefix, enstore_files):
    """
    Find the existing files in the directories mentioned in enstore_files
    """

    # FIXME: Need to centrally define these
    EOS_METHOD = 'XrdSecPROTOCOL=sss'
    EOS_KEYTAB = 'XrdSecSSSKT=/keytabs/ctafrontend_server_sss.keytab'
    EOS_HOST = 'storagedev201.fnal.gov'

    eos_directories = set()
    existing_files = set()
    for enstore_file in enstore_files:
        path_parts = enstore_file['pnfs_path'].split('/')
        eos_directory = cta_prefix + '/'.join(path_parts[:-1]) + '/'
        eos_directories.add(eos_directory)

    with open('/tmp/list_directories.eosh', 'w') as eosh:
        for eos_directory in eos_directories:
            eosh.write(f'cd {eos_directory}\n')
            eosh.write(f'pwd\n')
            eosh.write(f'ls\n')

    result = subprocess.run(['env', EOS_METHOD, EOS_KEYTAB,
                             'eos', '-r', '0', '0', f'root://{EOS_HOST}', '/tmp/list_directories.eosh'],
                            capture_output=True, text=True)
    """
    The format of the file is like this
    /path/to/directory
    file1
    file2
    /path/to/next/dir
    ...
    """

    current_dir = ''
    for line in result.stdout.split('\n'):
        if '/' in line:
            current_dir = line
        else:
            existing_files.add(os.path.normpath(current_dir + line))

    print(f'Checking {len(enstore_files)} EOS files: {len(existing_files)} in the {len(eos_directories)} directories')

    return existing_files


def insert_cta_files(engine, enstore_files, vid=VID_VALUE, cta_instance=CTA_INSTANCE):
    file_ids = {}

    number_in_cta = 0
    number_created = 0
    with engine.connect() as connection, Session(engine) as session:
        for enstore_file in enstore_files:
            file_name = enstore_file['pnfs_path']
            file_size = int(enstore_file['size'])
            enstore_fseq = int(enstore_file['location_cookie'].split('_')[2])  # pull off last field and make integer
            ef_dict = dict(enstore_file)
            uid = ef_dict.get('uid', 1000)
            gid = ef_dict.get('gid', 1000)
            eos_id = enstore_file['pnfs_id']
            _dummy, file_timestamp, _dummy = decode_bfid(enstore_file['bfid'])
            if file_timestamp < get_switch_epoch():
                adler_int, adler_string = convert_0_adler32_to_1_adler32(int(enstore_file['crc']), file_size)
            else:
                adler_int, adler_string = get_adler32_string(int(enstore_file['crc']))
            adler_blob = get_checksum_blob(adler_string)

            existing_file = connection.execute(select(ArchiveFile)
                                               .where(ArchiveFile.size_in_bytes == file_size)
                                               .where(ArchiveFile.checksum_adler32 == adler_int)).first()
            existing_tapefile = connection.execute(select(TapeFile)
                                                   .where(TapeFile.vid == vid)
                                                   .where(TapeFile.fseq == enstore_fseq)).first()

            if existing_file and existing_tapefile:
                number_in_cta += 1
                file_ids[file_name] = existing_file.archive_file_id
                continue

            archive_file = ArchiveFile(disk_instance_name=cta_instance, disk_file_id=eos_id, disk_file_uid=uid,
                                       disk_file_gid=gid, size_in_bytes=file_size, checksum_blob=adler_blob,
                                       checksum_adler32=adler_int, storage_class_id=1, creation_time=file_timestamp,
                                       reconciliation_time=file_timestamp, is_deleted='0')
            session.add(archive_file)
            session.flush()
            number_created += 1
            file_ids[file_name] = archive_file.archive_file_id

            tape_file = TapeFile(vid=vid, fseq=enstore_fseq, block_id=enstore_fseq,
                                 logical_size_in_bytes=file_size,
                                 copy_nb=1, creation_time=int(time.time()),
                                 archive_file_id=archive_file.archive_file_id)
            session.add(tape_file)
            update_counts(engine, volume_label=vid, bytes_written=file_size, fseq=enstore_fseq)

        session.commit()
        print(f'Creating {len(enstore_files)} files in CTA: {number_in_cta} already existed, {number_created} created.')
    return file_ids


def create_cta_tape(engine, vid=VID_VALUE, drive='VDSTK11', media_type=None, enstore_castor=None):
    # Create a new Enstore tape in DB or modify the tape to have Enstore format
    # FIXME: Figure out how to do media type, either translating from Enstore or external lookup or ....
    # FIXME: Have to build a migrator for the CASTOR formatted tapes too

    try:
        with Session(engine) as session:
            tape = create_m8_tape(vid=vid, drive=drive)
            session.add(tape)
            session.commit()
    except IntegrityError:
        with Session(engine) as session:
            stmt = (update(Tape)
                    .where(Tape.vid == vid)
                    .values(label_format=2)  # FIXME: This is not setting the tape to M8 yet
                    .execution_options(synchronize_session="fetch"))
            result = session.execute(stmt)
            session.commit()


def create_cta_tape_from_enstore(engine, volume, drive='Enstore'):
    # Create a new CTA-Enstore tape in DB or modify the tape to have Enstore format

    """
    Mattermost discussion on July 20
    What is a master file? I'm looking at the Tape schema and see this being tracked (number of files and bytes)


    Michael Davis
    It's just the number of files and number of bytes on the tape that have been written and not deleted.
    (I'm not really sure where the "master" nomenclature came from).

    The "master data in bytes" can be contrasted with "occupancy" which is the total number of bytes
    which have been written to date.
    master_data_in_bytes/occupancy is the ratio of not-deleted files to total occupancy,
    we use this metric to decide when a tape should be repacked.
    """

    media_map = {'M8': 'LTO7M',
                 'LTO8': 'LTO8'}

    label_format = 2
    if 'cern' in volume.wrapper:
        label_format = 0

    media_type = volume.media_type
    cta_media_name = media_map[media_type]

    # FIXME: Use with here
    cta_session = Session(engine)
    cta_media_type = cta_session.execute(select(MediaType).where(MediaType.media_type_name == cta_media_name)).first()[
        0]
    media_type_id = cta_media_type.media_type_id

    tape = Tape(vid=volume.label[0:6],
                media_type_id=media_type_id,
                vendor='Unknown',
                logical_library_id=1,  # FIXME: Get from Library
                tape_pool_id=1,  # FIXME
                encryption_key_name='',
                data_in_bytes=0,
                last_fseq=0,
                nb_master_files=0,
                master_data_in_bytes=0,
                is_full='1',  # FIXME: Set to full when migrated
                is_from_castor='0',
                dirty='0',
                nb_copy_nb_1=0,  # increment
                copy_nb_1_in_bytes=0,  # increment
                nb_copy_nb_gt_1=0,
                copy_nb_gt_1_in_bytes=0,
                label_format=label_format,
                label_drive=drive,
                label_time=int(volume.declared.timestamp()),
                last_read_drive=drive,
                last_read_time=int(volume.last_access.timestamp()),
                last_write_drive=drive,
                last_write_time=int(volume.last_access.timestamp()),
                read_mount_count=min(volume.sum_mounts, volume.sum_rd_access),
                write_mount_count=min(volume.sum_mounts, volume.sum_wr_access),
                user_comment=f'Migrated from Enstore: {volume.comment}',
                tape_state='ACTIVE',  # ACTIVE/DISABLED/BROKEN/REPACKING
                state_reason='Migrated from Enstore',
                state_update_time=int(time.time()),
                state_modified_by='Enstore migration',
                creation_log_user_name='Enstore migration',
                creation_log_host_name='enstore.fnal.gov',
                creation_log_time=int(time.time()),
                last_update_user_name='Enstore migration',
                last_update_host_name='enstore.fnal.gov',
                last_update_time=int(time.time()),
                verification_status='',
                )

    try:
        with Session(engine) as session:
            session.add(tape)
            session.commit()
    except IntegrityError:
        with Session(engine) as session:
            stmt = (update(Tape)
                    .where(Tape.vid == volume.label[0:6])
                    .values(label_format=label_format, media_type_id=media_type_id)
                    .execution_options(synchronize_session="fetch"))
            result = session.execute(stmt)
            session.commit()


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
                is_full='1',  # FIXME: Set to full when migrated
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


def enstore_files_from_csv(vid=VID_VALUE):
    enstore_files = []
    with open(f'../data/{vid}M8.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['pnfs_id'] = uuid.uuid4()  # Make up a dummy PNFS ID (assumes this is only for EOS migration)
            enstore_files.append(row)
    return enstore_files


def update_counts(engine, volume_label, bytes_written, fseq):
    """Update the tape byte and file counts on every insert"""
    with Session(engine) as session:
        tape = session.get(Tape, volume_label)  # New way. Check it works

        tape.copy_nb_1_in_bytes += bytes_written
        tape.master_data_in_bytes += bytes_written
        tape.data_in_bytes += bytes_written

        tape.nb_master_files += 1
        tape.nb_copy_nb_1 += 1

        tape.last_fseq = max(fseq, tape.last_fseq)
        session.commit()


main()
