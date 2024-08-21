#! /usr/bin/env bash


cp /etc/cta/forwardable.sss.keytab /etc/cta-nobody/
chmod 600 /etc/cta-nobody/forwardable.sss.keytab

/usr/sbin/td-agent -c /tdagent-config/td-agent-config
