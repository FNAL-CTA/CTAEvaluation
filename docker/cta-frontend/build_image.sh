#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/cta-frontend:5.11.2.fnal1
podman push imageregistry.fnal.gov/cta/cta-frontend:5.11.2.fnal1

