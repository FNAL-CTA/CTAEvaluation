#! /bin/bash

KRB5_CONFIG=/etc/krb5.cta.conf
KRB5CCNAME=/tmp/krb5cache

for FILE in $(eos ls -l /eos/archive/ewv/100k/ | grep "1000000" | awk '{print $NF}' ); do
  echo  /eos/archive/ewv/100k/"$FILE"
  xrdfs storagedev201.fnal.gov prepare -s /eos/archive/ewv/100k/"$FILE"
done
