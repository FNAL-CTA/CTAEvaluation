#! /bin/bash

KRB5_CONFIG=/etc/krb5.cta.conf
KRB5CCNAME=/tmp/krb5cache
NTIMES=100
FILESIZE=1000000

for i in $(seq $NTIMES); do
  FNAME=`mktemp -u -p /`
  head -c $FILESIZE </dev/urandom >/tmp/$FNAME
  xrdcp /tmp/$FNAME root://storagedev201.fnal.gov://eos/archive/ewv/100k/$FNAME
done
