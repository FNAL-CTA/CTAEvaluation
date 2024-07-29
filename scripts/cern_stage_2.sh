#! /bin/bash -e

set -x

# This script runs as CTA

cp ~/CTAEvaluation/replacements/00-cta-tape.rules ~/CTA/continuousintegration/ci_runner/00-cta-tape.rules
cp ~/CTAEvaluation/replacements/big_buffer_taped.sh ~/CTA/continuousintegration/docker/ctafrontend/opt/run/bin/taped.sh

cd ~/CTA
#git remote add ewv https://ewv@gitlab.cern.ch/ewv/CTA.git || echo "Already existed"
git fetch --all
git checkout 670-add-ability-to-read-enstore-large-file-tapes

cd ~/CTA/continuousintegration/ci_runner/vmBootstrap
./bootstrapCTA.sh

cd ~/CTA/continuousintegration/ci_runner/vmBootstrap
./bootstrapMHVTL.sh

echo "sudo reboot / ssh cta@ewv-cta /  ~/CTAEvaluation/scripts/cern_stage_2b.sh"
exit;

cd ~/CTA/continuousintegration/ci_runner/vmBootstrap
./bootstrapKubernetes.sh

echo "sudo reboot / ssh cta@ewv-cta /  ~/CTAEvaluation/scripts/cern_stage_3.sh"
