#! /bin/sh

podman build --net host . -t imageregistry.fnal.gov/cta/atresys:5.11.9.fnal2
# podman push imageregistry.fnal.gov/cta/cta-atresys-cron:5.11.9.fnal2