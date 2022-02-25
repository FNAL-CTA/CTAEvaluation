#! /bin/bash -e

set -x

# This script must run as CTA

cd ~/CTA/continuousintegration/buildtree_runner
./prepareImage.sh

cd ~/CTA/continuousintegration/buildtree_runner
sudo ./recreate_buildtree_running_environment.sh

kubectl -n cta get pv

cd ~/CTA/continuousintegration/orchestration
cp internal_postgres.yaml database.yaml

cp ~/CTAEvaluation/replacements/CERN/create_instance.sh .
sudo bash -xv ./create_instance.sh -n cta -b ~ -B CTA-build -D -O -d database.yaml
