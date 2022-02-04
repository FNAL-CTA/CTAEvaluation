#! /bin/bash

sudo mkdir /home/ewv
sudo chown ewv /home/ewv
cd /home/ewv

cp ~/CTAEvaluation/replacements/CERN/98-noipv6.conf /etc/sysctl.d/

sudo sysctl --system
sudo yum install -y git tmux nano

git clone https://gitlab.cern.ch/cta/CTA.git
cd CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapSystem.sh cta

sudo -u cta bash -c 'cd ~ ; git clone https://github.com/ericvaandering/CTAEvaluation.git'

su - cta

cp ~/CTAEvaluation/replacements/00-cta-tape.rules ~/CTA/continuousintegration/buildtree_runner/00-cta-tape.rules

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapCTA.sh

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapMHVTL.sh

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapKubernetes.sh

echo "sudo reboot; su - cta; next script"