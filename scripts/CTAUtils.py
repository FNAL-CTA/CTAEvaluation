#! /usr/bin/env python3
import os
import subprocess
import time
from typing import List, Tuple

import cta_common_pb2

from CTADatabaseModel import MediaType
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


# def adler_checksum(file_name: str) -> Tuple[int, str]:
#     from zlib import adler32
#     adler_sum = 1
#     with open(file_name, "rb") as file_handle:
#         # FIXME: Use Walrus operator for python 3.8 (while data := file_handle.read and no break)
#         while True:
#             data = file_handle.read(BLOCKSIZE)
#             if not data:
#                 break
#             adler_sum = adler32(data, adler_sum)
#     return adler_sum, hex(adler_sum)[2:10].zfill(8).lower()


def get_adler32_string(crc: int) -> Tuple[int, str]:
    """
    Similar signature to what is above, return back the value and the hex string
    """

    return crc, hex(crc)[2:10].zfill(8).lower()


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


def make_eos_subdirs(eos_files: List[str], sleep_time: int = 10, eos_prefix='/'):
    # FIXME: Refactor this to be part of EosInfo

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
        result = subprocess.run(['eos', 'root://localhost', 'mkdir', '-p', eos_directory], stdout=subprocess.PIPE)

    time.sleep(sleep_time)


def add_media_types(engine):
    media_types = [
        {'name': 'LTO7M', 'capacity': 9000000000000, 'cartridge': 'LTO-7',
         'comment': 'LTO-7 M8 cartridge formated at 9 TB', 'primary_density': 93},
        {'name': 'LTO8', 'capacity': 12000000000000, 'cartridge': 'LTO-8',
         'comment': 'LTO-8 cartridge formated at 12 TB', 'primary_density': 94},
    ]

    for media_type in media_types:
        media = MediaType(media_type_name=media_type['name'], capacity=media_type['capacity'],
                          user_comment=media_type['comment'], primary_density_code=media_type['primary_density'],
                          cartridge=media_type['cartridge'], creation_log_time=int(time.time()))

        try:
            with Session(engine) as session:
                session.add(media)
                session.commit()
        except IntegrityError:
            print(f'Media type {media_type["name"]} already existed')
