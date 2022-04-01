#! /bin/bash -e

# This script runs as the login user (does most things as root)

set -x

#sudo mkdir /home/ewv || true
#sudo chown ewv /home/ewv
#cd /home/ewv
#
#sudo cp ~/CTAEvaluation/replacements/CERN/98-noipv6.conf /etc/sysctl.d/
#
#sudo sysctl --system
yum install -y git tmux nano centos-release-scl
#sudo yum install -y git tmux nano pip3
#sudo pip3 install protobuf
#sudo pip3 install sqlalchemy

git clone https://gitlab.cern.ch/cta/CTA.git || true
cd CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapSystem.sh cta

sudo -u cta bash -c 'cd ~ ; git clone https://github.com/ericvaandering/CTAEvaluation.git'

echo "su - cta then ~/CTAEvaluation/scripts/cern_stage_2.sh"
