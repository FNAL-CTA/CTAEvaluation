#! /bin/bash -e

# This script runs as the login user (does most things as root)

set -x
yum install -y git tmux nano wget

ln -s /etc/pki/rpm-gpg/RPM-ASC-KEY-ceph /etc/pki/rpm-gpg/RPM-GPG-KEY-ceph

git clone https://gitlab.cern.ch/cta/CTA.git || true
cd ~/CTA

cd ~/CTA/continuousintegration/ci_runner/vmBootstrap
./bootstrapSystem.sh cta

sudo -u cta bash -c 'cd ~ ; git clone https://github.com/ericvaandering/CTAEvaluation.git; cd CTAEvaluation; git checkout ci_2024'

echo "su - cta then ~/CTAEvaluation/scripts/cern_stage_2.sh"
