#! /bin/bash -e

set -x

# This script runs as CTA

cp ~/CTAEvaluation/replacements/00-cta-tape.rules ~/CTA/continuousintegration/ci_runner/00-cta-tape.rules

cd ~/CTA
#git remote add ewv https://ewv@gitlab.cern.ch/ewv/CTA.git || echo "Already existed"
git fetch --all
git checkout 664-report-tape-label-format-cta-osm-enstore-in-cta-admin-tape-ls
git submodule init
git submodule update
cd xrootd-ssi-protobuf-interface
git remote add ewv https://ewv@gitlab.cern.ch/ewv/xrootd-ssi-protobuf-interface.git || echo "Already existed"
git fetch --all
git checkout ewv/cta-664

cd ~/CTA/continuousintegration/ci_runner/vmBootstrap
./bootstrapCTA.sh

cd ~/CTA/continuousintegration/ci_runner/vmBootstrap
./bootstrapMHVTL.sh

echo "sudo reboot / ssh cta@ewv-cta /  ~/CTAEvaluation/scripts/cern_stage_2b.sh"
exit;

cd ~/CTA/continuousintegration/ci_runner/vmBootstrap
./bootstrapKubernetes.sh

echo "sudo reboot / ssh cta@ewv-cta /  ~/CTAEvaluation/scripts/cern_stage_3.sh"
