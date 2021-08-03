#! /bin/bash

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapMHVTL.sh

cd ~/CTA/continuousintegration/buildtree_runner
./prepareImage.sh


cd ~/CTA/continuousintegration/buildtree_runner
sudo ./recreate_buildtree_running_environment.sh

echo "Make sure there are 3 PV entries here"
kubectl -n cta get pv