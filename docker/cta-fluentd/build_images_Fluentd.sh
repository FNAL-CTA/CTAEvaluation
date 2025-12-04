#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/cta-fluentd:5.11.13.fnal1
podman push imageregistry.fnal.gov/cta/cta-fluentd:5.11.13.fnal1

#podman build --net host . -f Containerfile.logs -t imageregistry.fnal.gov/cta/cta-logs-fluentd:0.0.1
#podman push imageregistry.fnal.gov/cta/cta-logs-fluentd:0.0.1
#
