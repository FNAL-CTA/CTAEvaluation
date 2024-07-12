#! /usr/bin/env bash

# Need a keytab owned by the OKD generic user, not readable by anyone
cp /etc/cta/eos.sss.keytab /etc/cta-nobody/
chmod 600 /etc/cta-nobody/eos.sss.keytab

# Start the server
/usr/bin/xrootd -l /var/log/cta/cta-frontend-xrootd.log -c /etc/cta/cta-frontend-xrootd.conf -k fifo -n cta
