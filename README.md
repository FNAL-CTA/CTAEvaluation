These are useful files and scripts for the FNAL evaluation of CTA


- Go to https://fcl1801.fnal.gov/dashboard/project/ 
- Select Project Services/storage
- Create new instance with 2 CPUs and 4 GB of RAM. Select the  and the sl7_smalldisk_v1 image
- Wait a few minutes to let puppet finish the node setup
`ssh root@[IP ADDRESS]` (take note of node name for future logins)
If logging in by IP doesn't work (doesn't work for Eric from home), do dig -x IP_ADDRESS to get the hostname and use that instead.

```commandline
git clone https://github.com/ericvaandering/CTAEvaluation.git
~/CTAEvaluation/scripts/bootstrap_k8s.sh (this runs as root)
```

then follow the instructions given to work through the other three stages. 
The other stages all run as CTA, so `su - cta` at the beginning. There is a reboot needed between stage 1 and stage 2 
There is a check that image creation worked between stage 2 and stage 3. I often find I need to restart docker again and run `prepareImage.sh` multiple times.

One everything is up and running you can then try running various tests like

```commandline
cd ~/CTA/continuousintegration/orchestration/tests/
./archive_retrieve.sh
```

or running individual commands on the CLI: `kubectl --n cta exec ctacli -- cta-admin tape ls --all`

In the case where authorizataion failed, you need to renew the kerberos token for the CLI with:
```commandline
kubectl -n cta exec ctacli -- kinit -kt /root/ctaadmin1.keytab ctaadmin1@TEST.CTA
```
(this differes a bit from what is in the documentation). 
You can also save a bit of time by invoking a shell directly on the client machine with 
```commandline
kubectl -n cta exec -it ctacli -- bash
```
and from there just issue cta-admin commands directly.