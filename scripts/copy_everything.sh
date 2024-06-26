#! /bin/bash

KRB5_CONFIG=/etc/krb5.cta.conf
KRB5CCNAME=/tmp/krb5cache

path="/eos/ctaeos/cta/"
replace="/eos/archive/"


for FILE in $(eos find -f /eos/ctaeos/cta/pnfs/fs/usr/cms/WAX/11/store/mc/RunIILowPUSpring18wmLHEGS/WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8/GEN-SIM/94X_mc2017_realistic_v10For2017H_v2_ext1-v1/); do
  #echo "${FILE/$path/$replace}"
  env KRB5_CONFIG=/etc/krb5.cta.conf KRB5CCNAME=/tmp/krb5cache  xrdcp  root://storagedev201/$FILE root://storagedev201/${FILE/$path/$replace}
done
#env KRB5_CONFIG=/etc/krb5.cta.conf KRB5CCNAME=/tmp/krb5cache  xrdcp  root://storagedev201//eos/ctaeos/cta/pnfs/fs/usr/cms/WAX/11/store/mc/RunIILowPUSpring18wmLHEGS/WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/GEN-SIM/94X_mc2017_realistic_v10For2017H_v2_ext1-v1/00000/403A0CD7-DE05-E911-9ED4-0242AC130002.root root://storagedev201//eos/archive/pnfs/fs/usr/cms/WAX/11/store/mc/RunIILowPUSpring18wmLHEGS/WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/GEN-SIM/94X_mc2017_realistic_v10For2017H_v2_ext1-v1/00000/403A0CD7-DE05-E911-9ED4-0242AC130002.root
