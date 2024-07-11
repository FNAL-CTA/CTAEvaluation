#! /bin/bash

KRB5_CONFIG=/etc/krb5.cta.conf
KRB5CCNAME=/tmp/krb5cache

for FILE in $(eos find -f /eos/ctaeos/cta/pnfs/fs/usr/cms/WAX/11/store/mc/RunIISummer19UL17HLT/GluGluToHiggs0PHf05ph0continToZZTo4tau_M125_GaSM_13TeV_MCFM701_pythia8/GEN-SIM-RAW/94X_mc2017_realistic_v15-v2/130000); do
  xrdfs storagedev201.fnal.gov prepare -s "$FILE"
done
