#! /bin/bash

# This will be replaced by something more permanent later

podman rm -f fluentd
podman run --name fluentd -v /var/log:/var/host-logs -v /root/ewv/CTAEvaluation/docker/cta-fluentd/frontend-td-agent.conf:/opt/bitnami/fluentd/conf/fluentd.conf imageregistry.fnal.gov/cta/cta-logs-fluentd:0.0.1
