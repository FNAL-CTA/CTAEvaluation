#! /usr/bin/env bash


# We need a copy of the key readable by the OKD user and no one else
cp /etc/cta/forwardable.sss.keytab /etc/cta-nobody/
chmod 600 /etc/cta-nobody/forwardable.sss.keytab

/CreateSCFromJSON
