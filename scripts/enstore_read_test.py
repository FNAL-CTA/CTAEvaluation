#! /usr/bin/env python3

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

VID_VALUE = 'VR1863'


ENSTORE_USER = os.getenv('ENSTORE_USER')
ENSTORE_PASSWORD = os.environ.get('ENSTORE_PASSWORD')
ENSTORE_HOST = os.getenv('ENSTORE_HOST')
ENSTORE_PORT = os.getenv('ENSTORE_PORT')

enstore_files = []

enstore = create_engine(f'postgresql://{ENSTORE_USER}:{ENSTORE_PASSWORD}@{ENSTORE_HOST}:{ENSTORE_PORT}/enstoredb',
                        echo=True,
                        future=True)
metadata_obj = MetaData()
EnstoreFiles = Table("file", metadata_obj, autoload_with=enstore)
EnstoreVolumes = Table("volume", metadata_obj, autoload_with=enstore)

with Session(enstore, future=True) as enstore_session:
    volume = enstore_session.execute(
        select(EnstoreVolumes).where(EnstoreVolumes.c.label == VID_VALUE + 'M8')).first()
    for row in enstore_session.execute(select(EnstoreFiles).where(EnstoreFiles.c.volume == volume.id)):
        import pdb; import pprint; pdb.set_trace()
        enstore_files.append(row)

# Make EOS directories for the files
eos_files = [enstore_file['pnfs_path'] for enstore_file in enstore_files]
