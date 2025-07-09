#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/storageclass-maker:1.0.2
podman push imageregistry.fnal.gov/cta/storageclass-maker:1.0.2

