#! /bin/bash

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapMHVTL.sh

echo "Wait, restarting docker engine"
sudo systemctl restart docker
#sudo systemctl restart kubelet


sleep 120

cd ~/CTA/continuousintegration/buildtree_runner
./prepareImage.sh

echo "Repeat ./prepareImage.sh as needed until it succeeds."
echo "May also need sudo systemctl restart docker"


kubectl exec -i -t dnsutils -- nslookup kubernetes.default
kubectl exec -i -t dnsutils -- nslookup www.cnn.com

echo "Once prepareImage has succeeded then ./CTAEvaluation/scripts/fnal_stage_3.sh"
