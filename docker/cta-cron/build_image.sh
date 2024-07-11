#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/cta-cron:latest
podman push imageregistry.fnal.gov/cta/cta-cron:latest

