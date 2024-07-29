#! /bin/bash

# FIXME: This works in that it creates a deployment and pod with cloudprober.
# But I think that the database is not allowing the connection from a pod, so in the end we get nothing.

kubectl create configmap cloudprober-postgres-config --from-file=cloudprober.cfg=cloudprober-postgres.cfg  -o yaml --dry-run=client | kubectl replace -f -

export CONFIG_CHECKSUM=$(kubectl get cm/cloudprober-postgres-config -o yaml | sha256sum) && cat cloudprober_postgres_deployment.yaml | envsubst | kubectl apply -f -
