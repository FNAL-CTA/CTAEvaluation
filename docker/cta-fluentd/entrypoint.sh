#! /usr/bin/env bash

# FIXME: Parameterize the krb.conf for the right KDC

#kinit -kt /keytabs/user1.keytab user1@TEST.CTA
#kinit -kt /keytabs/poweruser2.keytab poweruser2@TEST.CTA



#export EOSPOWER_USER="poweruser2"
#export EOSINSTANCE=storagedev201
#mkdir /tmp/${EOSPOWER_USER}
#KRB5CCNAME=/tmp/${EOSPOWER_USER}/krb5cc_0 kinit -kt /keytabs/${EOSPOWER_USER}.keytab ${EOSPOWER_USER}@TEST.CTA

#cp /etc-host/ctafrontend_forwardable_sss.keytab /etc/ctafrontend_client_sss.keytab
#chmod 700 /etc/ctafrontend_client_sss.keytab
CTA_INSTANCE=$CTA_INSTANCE /usr/sbin/td-agent -c /etc/td-agent/td-agent.conf 

#chmod o+rw /etc/ctafrontend_client_sss.keytab
#td-agent-gem install fluent-plugin-parser-logfmt
#
#CMD ["sudo LD_PRELOAD=/opt/td-agent/embedded/lib/libjemalloc.so /usr/sbin/td-agent -c /etc/td-agent/td-agent.conf --user td-agent --group td-agent"]
