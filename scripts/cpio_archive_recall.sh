#! /bin/sh

export EOSINSTANCE=ctaeos
export TEST_FILE_NAME=`uuidgen`
xrdcp /etc/group root://${EOSINSTANCE}//eos/ctaeos/cta/${TEST_FILE_NAME}

# Something here about getting my poweruser ticket to be able to do the prepare and copy

