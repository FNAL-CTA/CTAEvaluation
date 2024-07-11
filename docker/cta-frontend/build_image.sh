#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/cta-frontend:5.10.10.fnal0
podman push imageregistry.fnal.gov/cta/cta-frontend:5.10.10.fnal0

