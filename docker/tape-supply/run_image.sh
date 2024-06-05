#! /usr/bin/env bash

docker run --volume /etc/cta/cta-cli.conf:/etc/cta/cta-cli.conf \
           --volume /etc/cta/ctafrontend_forwardable_sss.keytab:/etc/cta/forwardable_sss.keytab \
           -e  XrdSecPROTOCOL=sss  -e XrdSecSSSKT=/etc/cta/forwardable_sss.keytab \
           --entrypoint /bin/bash -it imageregistry.fnal.gov/cta/tape-supply:latest
