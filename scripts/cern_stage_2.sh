#! /bin/bash -e

set -x

# FIXME: remove when Julien's patch is applied in March
#wget https://gitlab.cern.ch/cta/CTA/-/raw/7f65bd64bae493ffcd0bd5b1302f544c80b513c7/continuousintegration/docker/ctafrontend/cc7/etc/yum.repos.d-public/ceph.repo -O ~/CTA/continuousintegration/docker/ctafrontend/cc7/etc/yum.repos.d-public/ceph.repo

# This script runs as CTA


cp ~/CTAEvaluation/replacements/00-cta-tape.rules ~/CTA/continuousintegration/buildtree_runner/00-cta-tape.rules

cd ~/CTA
git remote add ewv https://ewv@gitlab.cern.ch/ewv/CTA.git
git fetch --all
git checkout ewv/219-ceph-rpm-repo-key-no-longer-available

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapCTA.sh

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapMHVTL.sh

echo "sudo reboot / ssh cta@ewv-cta /  ~/CTAEvaluation/scripts/cern_stage_2b.sh"
exit;

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapKubernetes.sh

echo "sudo reboot / ssh cta@ewv-cta /  ~/CTAEvaluation/scripts/cern_stage_3.sh"
