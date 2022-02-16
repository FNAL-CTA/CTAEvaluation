#! /bin/bash

# This script runs as CTA

cp ~/CTAEvaluation/replacements/00-cta-tape.rules ~/CTA/continuousintegration/buildtree_runner/00-cta-tape.rules

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapCTA.sh

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapMHVTL.sh

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapKubernetes.sh

echo "sudo reboot / ssh cta@ewv-cta /  ~/CTAEvaluation/scripts/cern_stage_3.sh"