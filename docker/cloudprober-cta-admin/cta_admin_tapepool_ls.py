#! /usr/bin/env python3

import subprocess
import json


def produce_prom_metric(metric_name, value, drive_list, labels):
  #loop over labels to get key,value pairs
  #remove drives that we do not care about with the if not
  #import pdb; pdb.set_trace()
  #print(len(labels))  
  #print(metric_name)
  label_list=[]
  for label in labels:
    #print(label)
    label_list+=[label+'="'+drive_list[label]+'"']
    #print(label_list)
  
  #if not 'driveName="DRIVE0"' in label_list:
  print(metric_name, end='')
  print('{',', '.join(label_list),end='')#,sep = ", "
  print('}', end='')
  print(f' {value}')
   

drLS_output = subprocess.check_output(["XrdSecPROTOCOL=sss XrdSecSSSKT=/etc/ctafrontend_client_sss.keytab cta-admin --json tapepool ls"], shell=True)

driveLS_dict = json.loads(drLS_output)

#print(driveLS_dict)

for drive_list in driveLS_dict:
    #extracting the value of the information from the dr ls cta-admin command
    #print(drive)
    num_tapes = int(drive_list['numTapes'])
    num_partial_tapes = int(drive_list['numPartialTapes'])
    num_physical_files= int(drive_list['numPhysicalFiles'])
    capacity_bytes= int(drive_list['capacityBytes'])
    data_bytes= int(drive_list['dataBytes'])
    

    #formatting to look like what parmethus wants
    DriveLSLabels=['name','vo'] 
    produce_prom_metric('tapepool_number_of_tapes', num_tapes, drive_list, labels=DriveLSLabels)
    produce_prom_metric('tapepool_number_of_partial_tapes', num_partial_tapes, drive_list,labels=DriveLSLabels)
    produce_prom_metric('tapepool_number_of_physical_files', num_physical_files, drive_list,labels=DriveLSLabels)
    produce_prom_metric('tapepool_capacity_in_bytes', capacity_bytes, drive_list,labels=DriveLSLabels)
    produce_prom_metric('tapepool_data_in_bytes', data_bytes, drive_list,labels=DriveLSLabels)
     
