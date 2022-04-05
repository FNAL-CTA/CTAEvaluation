#! /bin/sh
#FIXME: This is pretty ugly so I really want to get rid of it. Shared secrets seem like the way.
instance=cta 

echo -n "Configuring KDC clients (frontend, cli...) "
kubectl --namespace=${instance} exec kdc cat /etc/krb5.conf | kubectl --namespace=${instance} exec -i cms-testing --  bash -c "cat > /etc/krb5.conf"
kubectl --namespace=${instance} exec kdc cat /root/user1.keytab | kubectl --namespace=${instance} exec -i cms-testing --  bash -c "cat > /root/user1.keytab"
kubectl --namespace=${instance} exec kdc cat /root/poweruser1.keytab | kubectl --namespace=${instance} exec -i cms-testing --  bash -c "cat > /root/poweruser1.keytab; mkdir -p /tmp/poweruser1"
kubectl --namespace=${instance} exec cms-testing -- kinit -kt /root/user1.keytab user1@TEST.CTA
kubectl --namespace=${instance} exec cms-testing -- kinit -kt /root/poweruser1.keytab poweruser1@TEST.CTA


export TESTING_IP=`kubectl get pods -n cta cms-testing  -o "jsonpath={.status.podIP}"`
kubectl exec -it -n cta ctaeos -- eos -r 0 0 vid add gateway $TESTING_IP grpc     
