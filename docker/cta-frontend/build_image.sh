#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/cta-frontend:5.11.9.fnal1
podman push imageregistry.fnal.gov/cta/cta-frontend:5.11.9.fnal1

