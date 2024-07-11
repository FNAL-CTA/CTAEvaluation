#! /usr/bin/env bash

# Need a keytab owned by the OKD generic user, not readable by anyone
cp /etc/cta/eos.sss.keytab /etc/cta-nobody/
chmod 600 /etc/cta-nobody/eos.sss.keytab

# We don't need this long term, for local testing
cp /etc/cta/forwardable.sss.keytab /etc/cta-nobody/
chmod 600 /etc/cta-nobody/forwardable.sss.keytab

# Make a file-based OS, initialize it
mkdir /tmp/os
cta-objectstore-initialize /tmp/os

# Start it here

/usr/bin/xrootd -l /var/log/cta/cta-frontend-xrootd.log -c /etc/cta/cta-frontend-xrootd.conf -k fifo -n cta

# Remove this once it's working
sleep 120