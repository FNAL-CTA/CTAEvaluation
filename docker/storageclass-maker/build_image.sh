#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/storageclass-maker:0.3.1
podman push imageregistry.fnal.gov/cta/storageclass-maker:0.3.1

