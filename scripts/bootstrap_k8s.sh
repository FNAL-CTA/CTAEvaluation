#! /bin/bash

# Bootstrap the system

yum install -y nano tmux git
# This is not in any Repo (I think it a difference between SLF7 and Centos7)
yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/centos-release-scl-rh-2-3.el7.centos.noarch.rpm


cd ~
git clone https://gitlab.cern.ch/cta/CTA.git
adduser -g cta cta
pushd CTA/continuousintegration/buildtree_runner/vmBootstrap
./bootstrapSystem.sh cta
popd

# Should be run as root. Sets up the node with kuberenetes and docker (recent versions)

cp ~/CTAEvaluation/replacements/FNAL/kubernetes.repo /etc/yum.repos.d/kubernetes.repo

# Set up networking
sysctl net.ipv4.conf.all.forwarding=1
sysctl net.ipv6.conf.all.disable_ipv6=0
iptables -P FORWARD ACCEPT
iptables --flush
iptables -tnat --flush

# Turn of SELinux
setenforce 0
sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config

# Turn off swap
sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
swapoff -av

# Install and start docker
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io
#systemctl enable docker.service
#systemctl start docker.service
systemctl enable docker
systemctl start docker

# Restart docker with OK DNS and able to run kubernetes
cp ~/CTAEvaluation/replacements/FNAL/docker-daemon.json /etc/docker/daemon.json
systemctl daemon-reload
systemctl restart docker

# Install and start kuberenetes
yum install -y flannel etcd kubelet kubeadm kubectl --disableexcludes=kubernetes
systemctl enable kubelet
systemctl start kubelet

kubeadm init --pod-network-cidr=192.168.0.0/16
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
kubectl create -f https://docs.projectcalico.org/manifests/tigera-operator.yaml
kubectl create -f https://docs.projectcalico.org/manifests/custom-resources.yaml
echo "Sleeping 60 seconds. Next should show all calico pods running"
sleep 60
kubectl get pods -n calico-system
sleep 5
kubectl taint nodes --all node-role.kubernetes.io/master-

echo "Making sure DNS works in the cluster"
kubectl get nodes -o wide
kubectl apply -f https://k8s.io/examples/admin/dns/dnsutils.yaml
kubectl get pods
sleep 10
kubectl exec -i -t dnsutils -- nslookup kubernetes.default
kubectl exec -i -t dnsutils -- nslookup www.cnn.com
sleep 2

sudo -u cta bash -c 'cd ~ ; git clone https://github.com/ericvaandering/CTAEvaluation.git'
sudo -u cta bash -c 'mkdir ~/.kube'

cp /etc/kubernetes/admin.conf ~cta/.kube/config
chown cta ~cta/.kube/config

echo "Now su - cta and then ./CTAEvaluation/scripts/fnal_stage_1.sh"

