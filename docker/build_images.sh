#! /bin/sh

#kubectl config set-context --current --namespace=cta
kubectl config set-context gce-dev --user=cluster-admin --namespace=dev
kubectl config use-context gce-dev

#~/CTAEvaluation/scripts/build_csv_migrate.sh

#mkdir tmp
#
#cp ~cta/CTA-build/migration/gRPC/eos-test-file-inject tmp/
#cp ~cta/CTA-build/migration/gRPC/eos-import-files-csv tmp/

sudo docker build . -t ericvaandering/cms_testing:latest

#rm -rf tmp/


