
cd ~/CTA/continuousintegration/buildtree_runner
sudo ./recreate_buildtree_running_environment.sh

echo "Make sure there are 3 PV entries here"
kubectl -n cta get pv




    9  sudo systemctl restart docker
   10  ./prepareImage.sh
   11  cd ~/CTA/continuousintegration/buildtree_runner
   12  sudo ./recreate_buildtree_running_environment.sh
   13  kubectl -n cta get pv
   14  cd ~/CTA/continuousintegration/orchestration
   15  cp internal_postgres.yaml database.yaml
   16  cp ~/CTAEvaluation/replacements/FNAL/create_instance.sh .
   17  sudo bash -xv ./create_instance.sh -n cta -b ~ -B CTA-build -D -O -d database.yaml
   18  kubectl exec -i -t dnsutils -- nslookup kubernetes.default
   19  history
   20  kubectl get pods -n cta
   21  sudo systemctl restart kubelet
   22  kubectl get pods -n cta
   23  kubectl get pods --all-namespaces
   24  kubectl exec -i -t dnsutils -- nslookup kubernetes.default
   25  history
