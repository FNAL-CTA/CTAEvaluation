#! /usr/bin/env bash

docker network create --subnet=172.18.0.0/16 mynet123
docker run --net mynet123 --ip 172.18.0.22 -v /root/cta_keytabs/:/keytabs -it ericvaandering/cms_testing:latest bash
