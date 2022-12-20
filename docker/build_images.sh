#! /bin/sh

#kubectl config set-context --current --namespace=cta
kubectl config set-context gce-dev --user=cluster-admin --namespace=dev
kubectl config use-context gce-dev

#~/CTAEvaluation/scripts/build_csv_migrate.sh

#mkdir tmp
#
#cp ~cta/CTA-build/migration/gRPC/eos-test-file-inject tmp/
#cp ~cta/CTA-build/migration/gRPC/eos-import-files-csv tmp/

cp ~cta/build_rpm/RPM/RPMS/x86_64/cta-cli-4-4958535git71bda8fb.el7.cern.x86_64.rpm tmp/
cp ~cta/build_rpm/RPM/RPMS/x86_64/cta-lib-common-4-4958535git71bda8fb.el7.cern.x86_64.rpm tmp/

sudo docker build . -t ericvaandering/cms_testing:latest

#rm -rf tmp/

cp ../data/VR5775M8.csv ../data/VR5776M8.csv /tmp

