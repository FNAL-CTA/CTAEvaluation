#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/cta-frontend:5.11.13.fnal1
podman push imageregistry.fnal.gov/cta/cta-frontend:5.11.13.fnal1

