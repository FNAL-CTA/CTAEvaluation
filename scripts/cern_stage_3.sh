#! /bin/bash -e

set -x

# This script must run as CTA

cd ~/CTA/continuousintegration/ci_runner
./prepareImage.sh  ~/CTA-build/RPM/ dev

cd ~/CTA/continuousintegration/ci_runner
sudo ./recreate_ci_running_environment.sh

cd ~/CTA/continuousintegration/orchestration
cp internal_postgres.yaml database.yaml

export image_tag=dev
sudo ./create_instance.sh -n cta -i $image_tag -D -O -d database.yaml