#! /usr/bin/env python3

import filecmp
import time

SPACE = " "
ZERO = "0"
BLOCK_LEN_LIMIT = 99999
RECORD_LEN_LIMIT = 99999
BLOCK_LENGTH_L = 5
RECORD_LENGTH_L = 5
EPOCH_031 = 1643630451   # Seconds for a time during the day when our test files were written

def get_cent_digit(date_l):
    if date_l[0] < 2000:
        cent_digit = SPACE
        cent = 1900
    else:
        cent_digit = ZERO
        cent = 2000
    return cent, cent_digit


def get_date(now):
    if isinstance(now, int):
        date_l = time.gmtime(now)
        cent, cent_digit = get_cent_digit(date_l)
        # the format is cent_digit then year (2 chars), then julian day.
        # make the julian day be 3 chars long with preceeding 0's
        return "%s%s%s" % (cent_digit,
                           ("%2s" % (date_l[0] - cent,)).replace(" ", "0"),
                           ("%3s" % (date_l[7],)).replace(" ", "0"))
    elif isinstance(now, str):
        return now # assume it's already in the right format
    else:
        # this format means no time was specified
        cent, cent_digit = get_cent_digit(time.gmtime(time.time()))
        return "%s%s" % (cent_digit, 5 * ZERO)


class Label:

    def __init__(self):
        self.label = 4 * SPACE
        self.text = ""


class Label1(Label):

    def __init__(self, file_id, file_set_id, file_section_number,
                 file_seq_number, gen_number, gen_ver_number, creation_date,
                 expiration_date, file_access, block_count, implementation_id):
        super().__init__()
        self.file_id = file_id
        self.file_set_id = file_set_id
        self.file_section_number = file_section_number
        self.file_seq_number = file_seq_number
        self.gen_number = gen_number
        self.gen_ver_number = gen_ver_number
        self.creation_date = get_date(creation_date)
        self.expiration_date = get_date(expiration_date)
        self.file_access = file_access
        self.implementation_id = implementation_id
        self.reserved = ''
        self.block_count = block_count

    def data(self) -> bytes:
        self.text = (f'{self.label:4}{self.file_id:<17}{self.file_set_id:6}{self.file_section_number:04}'
                     + f'{self.file_seq_number:04}{self.gen_number:04}{self.gen_ver_number:02}{self.creation_date:6}'
                     + f'{self.expiration_date:6}{self.file_access:1}{self.block_count:06}{self.implementation_id:13}'
                     + f'{self.reserved:7}')

        return bytes(self.text, 'utf-8')


class Label2(Label):

    def __init__(self, record_format, block_length, record_length,
                 implementation_id, offset_length):
        super().__init__()

        self.record_format = record_format
        if block_length <= BLOCK_LEN_LIMIT:
            self.block_length = block_length
        else:
            self.block_length = 0
        if record_length <= RECORD_LEN_LIMIT:
            self.record_length = record_length
        else:
            self.record_length = 0
        self.implementation_id = implementation_id
        self.offset_length = offset_length
        self.reserved = 28 * SPACE

    def data(self) -> bytes:

        self.text = (f'{self.label:4}{self.record_format:1}{self.block_length:05}{self.record_length:05}'
                     + f'{" ":1}{" ":18}{self.implementation_id:2}{" ":14}'
                     + f'{self.offset_length:02}{" ":28}')
        return bytes(self.text, 'utf-8')


class UserLabel1(Label):

    def __init__(self, file_seq_number, block_length, record_length, site,
                 hostname, drive_mfg, drive_model, drive_serial_num):
        super().__init__()
        self.file_seq_number = file_seq_number
        self.block_length = block_length
        self.record_length = record_length
        self.site = site
        self.hostname = hostname
        self.drive_mfg = drive_mfg
        self.drive_model = drive_model
        self.drive_serial_num = drive_serial_num

    def data(self) -> bytes:
        self.text = (f'{self.label:4}{self.file_seq_number:010}{self.block_length:010}{self.record_length:010}'
                     + f'{self.site:8}{self.hostname:10}{self.drive_mfg:8}{self.drive_model:8}'
                     + f'{self.drive_serial_num:12}')
        return bytes(self.text, 'utf-8')


class VOL1(Label):
    """
    Class representing the VOL1 tape label
    """

    def __init__(self, volume_id='', owner_id='CASTOR'):
        """
        :param volume_id: The tape name
        :param owner_id: 'CASTOR' or 'ENSTORE'
        """

        super().__init__()
        self.label = "VOL1"
        self.volume_id = volume_id
        self.volume_access = ''
        self.reserved1 = ''
        self.implementation_id = ''
        self.owner_id = owner_id
        self.reserved2 = ''
        self.label_version = '3'

    # FIXME: Don't understand why '00' is there; matches what CTA does, not documentation
    def data(self) -> bytes:
        # format ourselves to be a string of length 80
        self.text = (f'{self.label:4}{self.volume_id:6}{self.volume_access:1}{self.reserved1:13}'
                     + f'{self.implementation_id:13}{self.owner_id:14}{self.reserved1:26}00{self.label_version:1}')

        return bytes(self.text, 'utf-8')


class HDR1(Label1):

    def __init__(self, file_id, file_set_id, file_section_number, file_seq_number, gen_number, gen_ver_number,
                 creation_date, expiration_date, file_access, block_count, implementation_id):
        super().__init__(file_id, file_set_id, file_section_number, file_seq_number, gen_number, gen_ver_number,
                         creation_date, expiration_date, file_access, block_count, implementation_id)
        self.label = "HDR1"


class EOF1(Label1):
    def __init__(self, file_id, file_set_id, file_section_number,
                 file_seq_number, gen_number, gen_ver_number, creation_date,
                 expiration_date, file_access, block_count,
                 implementation_id):
        super().__init__(file_id, file_set_id, file_section_number,
                         file_seq_number, gen_number, gen_ver_number,
                         creation_date, expiration_date, file_access,
                         block_count, implementation_id)
        self.label = "EOF1"
        self.block_count = block_count


class HDR2(Label2):

    def __init__(self, record_format, block_length, record_length,
                 implementation_id, offset_length):
        super().__init__(record_format, block_length, record_length,
                         implementation_id, offset_length)
        self.label = "HDR2"


class EOF2(Label2):

    def __init__(self, record_format, block_length, record_length,
                 implementation_id, offset_length):
        super().__init__(record_format, block_length, record_length,
                         implementation_id, offset_length)
        self.label = "EOF2"


class UHL1(UserLabel1):

    def __init__(self, file_seq_number, block_length, record_length, site,
                 hostname, drive_mfg, drive_model, drive_serial_num):
        super().__init__(file_seq_number, block_length, record_length,
                         site, hostname, drive_mfg, drive_model,
                         drive_serial_num)
        self.label = "UHL1"


class UTL1(UserLabel1):

    def __init__(self, file_seq_number, block_length, record_length, site,
                 hostname, drive_mfg, drive_model, drive_serial_num):
        super().__init__(file_seq_number, block_length, record_length,
                         site, hostname, drive_mfg, drive_model,
                         drive_serial_num)
        self.label = "UTL1"




def testVOL1():
    with open('/tmp/test', 'wb') as test_file:
        vol1 = VOL1(volume_id='V01007')
        test_file.write(vol1.data())

    assert filecmp.cmp('/tmp/test', '../data/AfterTest/test1.out')


def testHDR1():
    with open('/tmp/test', 'wb') as test_file:
        hdr1 = HDR1(file_id=1, file_set_id='V01007', file_section_number=1, file_seq_number=1, gen_number=1,
                    gen_ver_number=0, creation_date=EPOCH_031, expiration_date=EPOCH_031, file_access=' ',
                    block_count=0,
                    implementation_id='CASTOR 2.1.15')
        test_file.write(hdr1.data())

    assert filecmp.cmp('/tmp/test', '../data/AfterTest/test2.out')


def testHDR2():
    with open('/tmp/test', 'wb') as test_file:
        hdr2 = HDR2(record_format='F', block_length=0, record_length=0, implementation_id='P', offset_length=0)
        test_file.write(hdr2.data())

    assert filecmp.cmp('/tmp/test', '../data/AfterTest/test3.out')


def testEOF1():
    with open('/tmp/test', 'wb') as test_file:
        eof1 = EOF1(file_id=1, file_set_id='V01007', file_section_number=1, file_seq_number=1, gen_number=1,
                    gen_ver_number=0, creation_date=EPOCH_031, expiration_date=EPOCH_031, file_access=' ',
                    block_count=1,
                    implementation_id='CASTOR 2.1.15')
        test_file.write(eof1.data())

    assert filecmp.cmp('/tmp/test', '../data/AfterTest/test8.out')


def testEOF2():
    with open('/tmp/test', 'wb') as test_file:
        eof2 = EOF2(record_format='F', block_length=0, record_length=0, implementation_id='P', offset_length=0)
        test_file.write(eof2.data())

    assert filecmp.cmp('/tmp/test', '../data/AfterTest/test9.out')


def testUHL1():
    with open('/tmp/test', 'wb') as test_file:
        uhl1 = UHL1(file_seq_number=1, block_length=256 * 1024, record_length=256 * 1024, site='CTA',
                    hostname='TPSRV01',
                    drive_mfg='STK', drive_model='MHVTL', drive_serial_num='VDSTK11')
        test_file.write(uhl1.data())

    assert filecmp.cmp('/tmp/test', '../data/AfterTest/test4.out')


def testUTL1():
    with open('/tmp/test', 'wb') as test_file:
        utl1 = UTL1(file_seq_number=1, block_length=256 * 1024, record_length=256 * 1024, site='CTA',
                    hostname='TPSRV01',
                    drive_mfg='STK', drive_model='MHVTL', drive_serial_num='VDSTK11')
        test_file.write(utl1.data())

    assert filecmp.cmp('/tmp/test', '../data/AfterTest/test10.out')


testVOL1()
testHDR1()
testHDR2()
testEOF1()
testEOF2()
testUHL1()
testUTL1()
