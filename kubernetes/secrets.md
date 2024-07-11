kubectl create secret generic eos-sss --from-file=/etc/cta/eos.sss.keytab
kubectl create secret generic forwardable-sss --from-file=/etc/cta/ctafrontend_forwardable_sss.keytab
kubectl create secret generic migration-grpc --from-file=/etc/cta/eos.grpc.keytab
kubectl create secret generic cta-catalogue --from-file=/etc/cta/cta-catalogue.conf



kubectl create cm cloudprober-cta-admin-config --from-file=cloudprober-cta-admin.cfg 
kubectl create cm cloudprober-postgres-config --from-file=cloudprober-postgres.cfg 
