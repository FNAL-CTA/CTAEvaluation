#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/cloudprober-cta-admin:latest
podman push imageregistry.fnal.gov/cta/cloudprober-cta-admin:latest

