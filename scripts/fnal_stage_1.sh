#! /bin/bash

sudo yum -y install cmake3
sudo ln -s /usr/bin/cmake3 /usr/local/bin/cmake

cp ~/CTAEvaluation/replacements/00-cta-tape.rules ~/CTA/continuousintegration/buildtree_runner/00-cta-tape.rules
ln -s ~/CTA/cta.spec.in ~/cta.spec.in

# Problems with Ceph certificate on October 12, 2021

# Keep checking if this is really needed. Seems like an RPM was forgotten in security
sudo yum -y --disablerepo="*" --enablerepo="slf-primary" downgrade binutils

# Try without this
#cp ~/CTAEvaluation/replacements/FNAL/bootstrapCTA.sh ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapCTA.sh

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapMHVTL.sh

echo "Make sure DNS is still working"
kubectl exec -i -t dnsutils -- nslookup kubernetes.default
kubectl exec -i -t dnsutils -- nslookup www.cnn.com


echo "Next sudo reboot , su - cta, ./CTAEvaluation/scripts/fnal_stage_2.sh  which will rebuild MHVTL with an updated kernel"