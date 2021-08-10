
cd ~/CTA/continuousintegration/buildtree_runner
sudo ./recreate_buildtree_running_environment.sh

echo "Make sure there are 3 PV entries here"
kubectl -n cta get pv
sleep 5

cd ~/CTA/continuousintegration/orchestration
cp internal_postgres.yaml database.yaml
cp ~/CTAEvaluation/replacements/FNAL/create_instance.sh .
sudo bash -xv ./create_instance.sh -n cta -b ~ -B CTA-build -D -O -d database.yaml

