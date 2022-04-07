#! /bin/bash -e

set -x

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapMHVTL.sh

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapKubernetes.sh

echo "sudo reboot / ssh cta@ewv-cta /  ~/CTAEvaluation/scripts/cern_stage_3.sh"