#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/tape-supply:latest
podman push imageregistry.fnal.gov/cta/tape-supply:latest

