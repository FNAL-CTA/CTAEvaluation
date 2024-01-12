#! /usr/bin/env bash
#eos vid ls
#This outputs something like this:
#tident:"unix@10.88.0.6":gid => root
#tident:"unix@10.88.0.6":uid => root
#docker network create --subnet=172.18.0.0/16 mynet123
#docker run --net mynet123 --ip 172.18.0.22 -v /root/cta_keytabs/:/keytabs -it ericvaandering/cms_testing:latest bash
#docker run --ip 10.88.0.6   -v /root/cta_keytabs/:/keytabs -it ericvaandering/cms_testing:latest bash
podman run --ip 10.88.0.6   -v /etc/cta:/keytabs -it ericvaandering/cms_testing:latest bash


