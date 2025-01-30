#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/cta-upgrade:5.11.0.fnal1
podman push imageregistry.fnal.gov/cta/cta-upgrade:5.11.0.fnal1

