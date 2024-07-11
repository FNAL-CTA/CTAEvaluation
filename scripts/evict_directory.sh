#! /bin/bash

KRB5_CONFIG=/etc/krb5.cta.conf
KRB5CCNAME=/tmp/krb5cache

for FILE in $(eos ls -l /eos/archive/ewv/100k/ | awk '{print $NF}' ); do
  echo  /eos/archive/ewv/100k/"$FILE"
  xrdfs storagedev201.fnal.gov prepare -e /eos/archive/ewv/100k/"$FILE"
done
