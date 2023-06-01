#! /usr/bin/env python3


from EnstoreUtils import get_switch_epoch, convert_0_adler32_to_1_adler32, decode_bfid

expected='47fe3c33'
actual='c3033c34'
file_size = 2774714801

found_int = int(expected, 16)

adler_int, adler_string = convert_0_adler32_to_1_adler32(found_int, file_size)

print (f'Expect: {adler_string}, got {actual}')
