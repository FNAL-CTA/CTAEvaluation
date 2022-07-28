#! /usr/bin/env bash

# FIXME: Parameterize the krb.conf for the right KDC

kinit -kt /keytabs/user1.keytab user1@TEST.CTA
kinit -kt /keytabs/poweruser1.keytab poweruser1@TEST.CTA



export EOSPOWER_USER="poweruser2"
export EOSINSTANCE=storagedev201
mkdir /tmp/${EOSPOWER_USER}
KRB5CCNAME=/tmp/${EOSPOWER_USER}/krb5cc_0 kinit -kt /keytabs/${EOSPOWER_USER}.keytab ${EOSPOWER_USER}@TEST.CTA

