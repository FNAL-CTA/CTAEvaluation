#! /bin/sh

set -x

export NAMESPACE=cta
cd ~/CTA/continuousintegration/orchestration || exit
./delete_instance.sh -n cta; sleep 30; sudo bash -xv ./create_instance.sh -n cta -b ~ -B CTA-build -D -O -d database.yaml
cd tests/ || exit
sleep 15
./prepare_tests.sh -n ${NAMESPACE}
kubectl -n ${NAMESPACE} cp simple_client_ar.sh client:/root/simple_client_ar.sh
kubectl -n ${NAMESPACE} cp client_helper.sh client:/root/client_helper.sh
kubectl -n ${NAMESPACE} cp ~/CTAEvaluation/scripts/cpio_archive_recall.sh client:/root/cpio_archive_recall.sh

kubectl exec -it -n cta client -- bash
