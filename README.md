These are useful files and scripts for the FNAL evaluation of CTA


Go to https://fcl1801.fnal.gov/dashboard/project/ 
Select Project Services/storage
Create new instance with type 4medium and image standard_sl7v9

Wait a few minutes to let puppet finish the node setup
ssh root@[IP ADDRESS] (take note of node name for future logins)

git clone https://github.com/ericvaandering/CTAEvaluation.git
~/CTAEvaluation/scripts/bootstrap_k8s.sh (this runs as root)
 
then follow the instructions given to work through the other three stages. 
The other stages all run as CTA, so su - cta at the beginning. There is a reboot needed between stage 1 and stage 2 
There is a check that image creation worked between stage 2 and stage 3. I often find I need to restart docker again and run prepareImage multiple times

