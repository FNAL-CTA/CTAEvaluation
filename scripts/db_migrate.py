#! /usr/bin/env python3

import binascii
import csv
import json
import os
import subprocess
import time
from typing import Tuple
from zlib import adler32

from sqlalchemy import create_engine, text

import cta_common_pb2

FILES_TO_READ = ['/etc/group']
BLOCKSIZE = 256 * 1024 * 1024
EOS_SERVER = 'ctaeos'  # FIXME: Get from config
CTA_PREFIX = 'eos/ctaeos/cta/'


class EosInfo:
    def __init__(self):
        self.eos_ids = {}

    def id_for_file(self, path: str) -> int:
        """
        Cache and retrieve the IDs of a path

        :param path: The full path of the file or directory to get the ID for
        :return: the ID number of the path
        """
        if path in self.eos_ids:
            return self.eos_ids[path]
        eos_url = f"root://{EOS_SERVER}"
        result = subprocess.run(['eos', '--json', eos_url, 'info', path], stdout=subprocess.PIPE)
        eos_info = json.loads(result.stdout.decode('utf-8'))
        try:
            self.eos_ids[path] = eos_info['id']
        except KeyError:
            return None
        return self.eos_ids[path]

    # eos --json root://ctaeos info /eos/ctaeos/cta


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


def get_checksum_blob(adler32: str):
    csb = cta_common_pb2.ChecksumBlob()

    my_cs = csb.cs.add()
    my_cs.type = my_cs.ADLER32
    adler32_r = adler32[6:8] + adler32[4:6] + adler32[2:4] + adler32[0:2]
    my_cs.value = bytes.fromhex(adler32_r)

    binascii.hexlify(csb.SerializeToString())
    return csb


def main():
    eos_info = EosInfo();
    # FIXME: Temporary just to show we have a DB connection
    engine = create_engine('postgresql://cta:cta@postgres/cta')
    with engine.connect() as conn:
        result = conn.execute(text("select 'hello world'"))
        print(result.all())

    with open('eos_files.csv', 'w', newline='') as csvfile:
        eos_file_inserts = csv.writer(csvfile)
        for file_name in FILES_TO_READ:
            uid = 1000
            gid = 1000
            enstore_id = 0
            file_size = os.path.getsize(file_name)
            adler_int, adler_string = adler_checksum(file_name)
            ctime = mtime = int(time.time())

            # Get the EOS container ID and set all paths correctly
            destination_file = os.path.normpath(CTA_PREFIX + '/' + file_name)
            eos_directory, base_file = os.path.split(destination_file)
            short_directory, base_file = os.path.split(file_name)
            container_id = eos_info.id_for_file(eos_directory)

            eos_file_inserts.writerow([enstore_id, container_id, uid, gid, file_size, adler_string,
                                 ctime, mtime, short_directory, base_file])


main()
