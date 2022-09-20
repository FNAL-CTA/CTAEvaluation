#! /usr/bin/env python3

import os
import re
import time
from typing import Tuple

CRC_SWITCH = '2019-08-21 09:54:26'


def get_switch_epoch():
    """
    Figure out the timestamp when the change from 0 to 1 based adler checksum happened
    """
    time_format = '%Y-%m-%d %H:%M:%S'
    os.environ['TZ'] = 'UTC'
    epoch = int(time.mktime(time.strptime(CRC_SWITCH, time_format)))

    return epoch


def decode_bfid(bfid: str) -> Tuple[str, int, int]:
    """
    E.g. CDMS156627743300000
    Letters are the brand
    Next 10 are the unix timestamp
    Remainder are the count
    """

    match = re.search(r'(\D+)(\d+)', bfid)

    brand = match.group(1)
    epoch = int(match.group(2)[0:10])
    count = int(match.group(2)[10:])

    return brand, epoch, count


def convert_0_adler32_to_1_adler32(crc: int, filesize: int) -> Tuple[int, str]:
    """
    Dmitry:
    OK, I did some archaelogy.
    the switchover to seed 1 occured on 2019-08-21 09:54:26.
    It was a downtime day. So all files wih update datestamp < 2019-08-21 09:54:26 have crc seeded 0,
    Anything newer - seed 1 (no new data was written until 11 AM on that day).

    From Ren: The BFID contains the update timestamp
    """

    BASE = 65521

    size = filesize % BASE
    s1 = (crc & 0xffff)
    s2 = ((crc >> 16) & 0xffff)
    s1 = (s1 + 1) % BASE
    s2 = (size + s2) % BASE
    new_adler = (s2 << 16) + s1
    return new_adler, hex(new_adler)[2:10].zfill(8).lower()
