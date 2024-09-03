#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/storageclass-maker:0.1.0
podman push imageregistry.fnal.gov/cta/storageclass-maker:0.1.0

