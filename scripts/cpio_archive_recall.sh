#! /bin/sh

set -x

. /root/client_helper.sh
eospower_kdestroy
eospower_kinit

export EOSINSTANCE=ctaeos
export TEST_FILE_NAME=`uuidgen`
xrdcp /etc/group root://${EOSINSTANCE}//eos/ctaeos/cta/${TEST_FILE_NAME}

# Something here about getting my poweruser ticket to be able to do the prepare and copy

XrdSecPROTOCOL=sss eos -r 0 0 root://${EOSINSTANCE} file drop /eos/ctaeos/cta/${TEST_FILE_NAME} 1

sleep 15
KRB5CCNAME=q/tmp/${EOSPOWER_USER}/krb5cc_0 XrdSecPROTOCOL=krb5 xrdfs ${EOSINSTANCE} prepare -s /eos/ctaeos/cta/${TEST_FILE_NAME}
sleep 15

xrdcp  root://${EOSINSTANCE}//eos/ctaeos/cta/${TEST_FILE_NAME} /root/test-group
