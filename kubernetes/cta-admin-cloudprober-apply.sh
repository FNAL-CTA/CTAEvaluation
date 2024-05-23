#! /bin/bash

kubectl create configmap cloudprober-cta-admin-config --from-file=cloudprober-cta-admin.cfg=cloudprober-cta-admin.cfg  -o yaml --dry-run | kubectl replace -f -

export CONFIG_CHECKSUM=$(kubectl get cm/cloudprober-cta-admin-config -o yaml | sha256sum) && cat cloudprober_cta_admin_deployment.yaml | envsubst | kubectl apply -f -

