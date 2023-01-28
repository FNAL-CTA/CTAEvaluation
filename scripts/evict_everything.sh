#! /bin/bash

KRB5_CONFIG=/etc/krb5.cta.conf
KRB5CCNAME=/tmp/krb5cache

for FILE in $(eos find -f /eos/ctaeos/cta/pnfs/fs/usr/cms/WAX/11/store/mc/); do
  xrdfs storagedev201.fnal.gov prepare -e "$FILE"
done
