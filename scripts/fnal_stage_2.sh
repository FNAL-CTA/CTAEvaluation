#! /bin/bash

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapMHVTL.sh


sudo systemctl restart docker
sudo systemctl restart kubelet

cd ~/CTA/continuousintegration/buildtree_runner
./prepareImage.sh

echo "Repeat ./prepareImage.sh as needed until it succeeds."
echo "May also need sudo systemctl restart docker"


kubectl exec -i -t dnsutils -- nslookup kubernetes.default
kubectl exec -i -t dnsutils -- nslookup www.cnn.com




