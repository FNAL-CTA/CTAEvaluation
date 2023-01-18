#! /usr/bin/env python3

import csv
import json
import os
import subprocess
import time

from sqlalchemy import MetaData, Table, create_engine, select, update, func, Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from CTADatabaseModel import ArchiveFile, MediaType, TapeFile, Tape
from CTAUtils import get_adler32_string, get_checksum_blob, make_eos_subdirs, add_media_types
from EnstoreUtils import get_switch_epoch, convert_0_adler32_to_1_adler32, decode_bfid
from EosInfo import EosInfo
from MigrationConfig import MigrationConfig

CTA_INSTANCE = 'ctaeos'
CTA_INSTANCE = 'eosdev'  # FIXME
VID_VALUE = 'VR7007'  # 'VR5775'
VID_VALUE = 'VR5775'

MIGRATION_CONF = '/CTAEvaluation/replacements/migration.conf'

SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.environ.get('SQL_PASSWORD')
SQL_HOST = os.getenv('SQL_HOST')
SQL_PORT = os.getenv('SQL_PORT')
SQL_DB = os.getenv('SQL_DB')

ENSTORE_USER = os.getenv('ENSTORE_USER')
ENSTORE_PASSWORD = os.environ.get('ENSTORE_PASSWORD')
ENSTORE_HOST = os.getenv('ENSTORE_HOST')

EOS_INSERT_LIST = '/tmp/eos-insert-list.json'

FROM_ENSTORE = False
FROM_CSV = True


def main():
    config = MigrationConfig(MIGRATION_CONF)
    eos_server = config.values['eos.endpoint'].split(':')[0]  # Just hostname. The port is probably gRPC
    cta_prefix = config.values['eos.prefix']
    eos_info = EosInfo(eos_server)

    engine = create_engine(f'postgresql://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}', echo=True)

    # Pre-setup
    add_media_types(engine=engine)

    # This is how we read from a file
    if FROM_CSV:
        enstore_files = enstore_files_from_csv(vid=VID_VALUE)
        enstore_files = enstore_files[0:20]  # Safe even if it's shorter
        create_cta_tape(engine=engine, vid=VID_VALUE)

    if FROM_ENSTORE:
        enstore = create_engine(f'postgresql://{ENSTORE_USER}:{ENSTORE_PASSWORD}@{ENSTORE_HOST}/dmsen_enstoredb',
                                echo=True,
                                future=True)
        metadata_obj = MetaData()
        EnstoreFiles = Table("file", metadata_obj, autoload_with=enstore)
        EnstoreVolumes = Table("volume", metadata_obj, autoload_with=enstore)

        with Session(enstore, future=True) as enstore_session:
            volume = enstore_session.execute(
                select(EnstoreVolumes).where(EnstoreVolumes.c.label == VID_VALUE + 'M8')).first()
            for row in enstore_session.execute(select(EnstoreFiles).where(EnstoreFiles.c.volume == volume.id)):
                enstore_files.append(row)
        create_cta_tape_from_enstore(engine, volume)

    file_ids = insert_cta_files(cta_prefix, engine, enstore_files)

    # Make EOS directories for the files
    eos_files = [enstore_file['pnfs_path'] for enstore_file in enstore_files]
    make_eos_subdirs(eos_prefix=cta_prefix, eos_files=eos_files)

    # Make EOS file placeholders for the files
    create_eos_files_new(cta_prefix, enstore_files, eos_info, file_ids)
    return
    # No longer needed, done automatically
    update_eos_fileids(cta_prefix, engine, enstore_files, eos_info, file_ids)


def update_eos_fileids(cta_prefix, engine, enstore_files, eos_info, file_ids):
    # Update the EOS ID for the files just inserted
    with Session(engine) as session:
        for enstore_file in enstore_files:
            file_name = enstore_file['pnfs_path']
            eos_file = os.path.normpath(cta_prefix + '/' + file_name)
            print(f"Checking EOS ID for {eos_file}")
            eos_id = eos_info.id_for_file(eos_file)
            if eos_id:
                archive_file_id = file_ids[file_name]
                stmt = (update(ArchiveFile)
                        .where(ArchiveFile.archive_file_id == archive_file_id)
                        .values(disk_file_id=eos_id)
                        .execution_options(synchronize_session="fetch"))

                result = session.execute(stmt)
            else:
                print(f'ERROR: {eos_file} has no ID (probably not created in EOS). Not linked in CTA database.')
        session.commit()


def create_eos_files(cta_prefix, enstore_files, eos_info, file_ids):
    # Build the list of files for EOS to insert
    with open('/tmp/eos_files.csv', 'w') as csvfile, open(EOS_INSERT_LIST, 'a') as jsonfile:
        eos_file_inserts = csv.writer(csvfile, lineterminator='\n')
        for enstore_file in enstore_files:
            file_name = enstore_file['pnfs_path']
            ef_dict = dict(enstore_file)
            uid = ef_dict.get('uid', 1000)
            gid = ef_dict.get('gid', 1000)
            enstore_id = enstore_file['bfid']
            enstore_id = enstore_id.replace('GCMS', '01')  # EOS wants an integer for the value. Map it.
            file_size = int(enstore_file['size'])
            _dummy, file_timestamp, _dummy = decode_bfid(enstore_file['bfid'])
            if file_timestamp < get_switch_epoch():
                adler_int, adler_string = convert_0_adler32_to_1_adler32(int(enstore_file['crc']), file_size)
            else:
                adler_int, adler_string = get_adler32_string(int(enstore_file['crc']))
            ctime = mtime = int(file_timestamp)

            # Get the EOS container ID and set all paths correctly
            destination_file = os.path.normpath(cta_prefix + '/' + file_name)
            eos_directory, base_file = os.path.split(destination_file)
            short_directory, base_file = os.path.split(file_name)
            container_id = eos_info.id_for_file(eos_directory)
            archive_file_id = file_ids[file_name]

            eos_file_inserts.writerow([enstore_id, container_id, uid, gid, file_size, adler_string,
                                       ctime, mtime, short_directory, base_file, archive_file_id])

            new_eos_file = {'eosPath': file_name, 'diskInstance': CTA_INSTANCE, 'archiveId': archive_file_id,
                            'size': file_size, 'checksumType': 'ADLER32', 'checksumValue': adler_string,
                            'enstoreId': enstore_id}
            jsonfile.write(json.dumps(new_eos_file))

    # Actually insert the files into EOS
    #   result = subprocess.run(['/root/eos-import-files-csv', '-c', MIGRATION_CONF], stdout=subprocess.PIPE)
    # Follow https://gitlab.cern.ch/cta/CTA/-/merge_requests/112/diffs#0d61d61ea27a782f8ca977f3003cb3dd4afa59af


def create_eos_files_new(cta_prefix, enstore_files, eos_info, file_ids):
    # Duplicated in CTAUtils.py

    EOS_METHOD = 'XrdSecPROTOCOL=sss'
    EOS_KEYTAB = 'XrdSecSSSKT=/keytabs/ctafrontend_server_sss.keytab'

    files_need_creating = False

    # Build the list of files for EOS to insert
    with open(EOS_INSERT_LIST, 'a') as jsonfile:
        for enstore_file in enstore_files:
            file_name = enstore_file['pnfs_path']
            enstore_id = enstore_file['bfid']
            enstore_id = enstore_id.replace('GCMS', '01')  # EOS wants an integer for the value. Map it.
            file_size = int(enstore_file['size'])
            _dummy, file_timestamp, _dummy = decode_bfid(enstore_file['bfid'])
            if file_timestamp < get_switch_epoch():
                adler_int, adler_string = convert_0_adler32_to_1_adler32(int(enstore_file['crc']), file_size)
            else:
                adler_int, adler_string = get_adler32_string(int(enstore_file['crc']))

            # Get the EOS container ID and set all paths correctly
            destination_file = os.path.normpath(cta_prefix + '/' + file_name)
            archive_file_id = file_ids[file_name]
            if not eos_info.id_for_file(destination_file):
                files_need_creating = True
                new_eos_file = {'eosPath': destination_file, 'diskInstance': CTA_INSTANCE,
                                'archiveId': str(archive_file_id), 'size': str(file_size), 'checksumType': 'ADLER32',
                                'checksumValue': adler_string, 'enstoreId': enstore_id}
                jsonfile.write(json.dumps(new_eos_file) + '\n')
            else:
                print(f'File {destination_file} already exists. Skipping.')

    # Actually insert the files into EOS
    if files_need_creating:
        result = subprocess.run(['env', EOS_METHOD, EOS_KEYTAB, 'cta-eos-namespace-inject', '--json', EOS_INSERT_LIST],
                                stdout=subprocess.PIPE)


def insert_cta_files(cta_prefix, engine, enstore_files, vid=VID_VALUE, cta_instance=CTA_INSTANCE):
    file_ids = {}
    with Session(engine) as session:
        # FIXME: Use the actual largest number plus some as the start value
        max_disk_file_id = int(session.execute(
            select(func.max(ArchiveFile.disk_file_id.cast(Integer)))
        ).scalar())

        for eos_id, enstore_file in enumerate(enstore_files, start=max_disk_file_id + 1000):
            file_name = enstore_file['pnfs_path']
            file_size = int(enstore_file['size'])

            ef_dict = dict(enstore_file)
            uid = ef_dict.get('uid', 1000)
            gid = ef_dict.get('gid', 1000)
            _dummy, file_timestamp, _dummy = decode_bfid(enstore_file['bfid'])
            if file_timestamp < get_switch_epoch():
                adler_int, adler_string = convert_0_adler32_to_1_adler32(int(enstore_file['crc']), file_size)
            else:
                adler_int, adler_string = get_adler32_string(int(enstore_file['crc']))
            adler_blob = get_checksum_blob(adler_string)

            # FIXME: Try catch here to continue on if the file is already inserted

            existing_file = engine.execute(select(ArchiveFile)
                                           .where(ArchiveFile.size_in_bytes == file_size)
                                           .where(ArchiveFile.checksum_adler32 == adler_int)).first()
            if existing_file:
                print(f"File existed is {existing_file.archive_file_id}")
                file_ids[file_name] = existing_file.archive_file_id
                # FIXME: We could also double check the TapeFile if needed
                continue

            archive_file = ArchiveFile(disk_instance_name=cta_instance, disk_file_id=eos_id, disk_file_uid=uid,
                                       disk_file_gid=gid, size_in_bytes=file_size, checksum_blob=adler_blob,
                                       checksum_adler32=adler_int, storage_class_id=1, creation_time=file_timestamp,
                                       reconciliation_time=file_timestamp, is_deleted='0')
            session.add(archive_file)
            session.flush()
            print(f"File inserted is {archive_file.archive_file_id}")
            file_ids[file_name] = archive_file.archive_file_id
            enstore_fseq = int(enstore_file['location_cookie'].split('_')[2])  # pull off last field and make integer

            print(f"Putting this file at FSEQ {enstore_fseq}")

            tape_file = TapeFile(vid=vid, fseq=enstore_fseq, block_id=enstore_fseq,
                                 logical_size_in_bytes=file_size,
                                 copy_nb=1, creation_time=int(time.time()),
                                 archive_file_id=archive_file.archive_file_id)
            session.add(tape_file)
            update_counts(engine, volume_label=vid, bytes_written=file_size, fseq=enstore_fseq)

        session.commit()
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
    cta_media_type = engine.execute(select(MediaType).where(MediaType.name == cta_media_name)).first()
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
                is_full='0',  # FIXME: Set to full when migrated
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


def enstore_files_from_csv(vid=VID_VALUE):
    enstore_files = []
    with open(f'../data/{VID_VALUE}M8.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            enstore_files.append(row)
    return enstore_files


def update_counts(engine, volume_label, bytes_written, fseq):
    """Update the tape byte and file counts on every insert"""
    with Session(engine) as session:
        # tape = engine.execute(select(Tape).where(Tape.vid == volume_label)).first()
        tape = session.query(Tape).get(volume_label)

        tape.copy_nb_1_in_bytes += bytes_written
        tape.master_data_in_bytes += bytes_written
        tape.data_in_bytes += bytes_written

        tape.nb_master_files += 1
        tape.nb_copy_nb_1 += 1

        tape.last_fseq = max(fseq, tape.last_fseq)
        session.commit()

    """
    something like....
    session = Session()
    u = session.query(User).get(123)
    u.name = u"Bob Marley"
    session.commit()"""


def test_enstore_read():
    VID_VALUE = 'VR7007'

    import pdb

    metadata_obj = MetaData()
    enstore = create_engine(f'postgresql://{ENSTORE_USER}:{ENSTORE_PASSWORD}@{ENSTORE_HOST}/dmsen_enstoredb', echo=True,
                            future=True)

    EnstoreFiles = Table("file", metadata_obj, autoload_with=enstore)
    EnstoreVolumes = Table("volume", metadata_obj, autoload_with=enstore)

    pdb.set_trace()

    with Session(enstore, future=True) as enstore_session:
        volume = enstore_session.execute(
            select(EnstoreVolumes).where(EnstoreVolumes.c.label == VID_VALUE + 'M8')).first()
        pdb.set_trace()
        for row in enstore_session.execute(select(EnstoreFiles).where(EnstoreFiles.c.volume == volume.id)):
            print(row)
            pdb.set_trace()
            # Both of these work
            print(row.bfid)
            print(row['bfid'])


# test_enstore_read()
main()
