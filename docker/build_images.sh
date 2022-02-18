#! /bin/sh

mkdir tmp

cp /home/cta/CTA-build/migration/gRPC/eos-test-file-inject tmp/

sudo docker build . -t ericvaandering/cms_testing:latest

rm -rf tmp/


