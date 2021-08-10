#! /bin/bash


cp ~/CTAEvaluation/replacements/00-cta-tape.rules ~/CTA/continuousintegration/buildtree_runner/00-cta-tape.rules
cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapCTA.sh

cd ~/CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapMHVTL.sh

echo "Make sure DNS is still working"
kubectl exec -i -t dnsutils -- nslookup kubernetes.default
kubectl exec -i -t dnsutils -- nslookup www.cnn.com


echo "We must reboot and continue with stage 2 which will rebuild MHVTL with an updated kernel"