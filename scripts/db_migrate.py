#! /usr/bin/env python3

import cta_common_pb2

import binascii
from sqlalchemy import create_engine, text

def get_checksum_blob(adler32):
    csb = cta_common_pb2.ChecksumBlob()

    my_cs = csb.cs.add()

    my_cs.type=my_cs.ADLER32

    adler32 = "20ce7e60"
    adler32_r = adler32[6:8]+adler32[4:6]+adler32[2:4]+adler32[0:2]
    my_cs.value = bytes.fromhex(adler32_r)




    binascii.hexlify(csb.SerializeToString())
    adler_int = int(adler32, 16)
    return csb


engine = create_engine('postgresql://cta:cta@postgres/cta')
with engine.connect() as conn:
   result = conn.execute(text("select 'hello world'"))
   print(result.all())