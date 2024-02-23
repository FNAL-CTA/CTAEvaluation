#! /usr/bin/env python3

import subprocess
import json


def produce_prom_metric(metric_name, metric_value, list_input, labels):
  #loop over labels to get key,value pairs
  #remove drives that we do not care about with the if not
  #import pdb; pdb.set_trace()
  #print(len(labels))  
  #print(metric_name)
  label_list=[]
  for label in labels:
    #print(label)
    label_list+=[label+'="'+list_input[label]+'"']
    #print(label_list)
  
  #if not 'driveName="DRIVE0"' in label_list:
  print(metric_name, end='')
  print('{',', '.join(label_list),end='')#,sep = ", "
  print('}', end='')
  print(f' {metric_value}')
   

cta_admin_output = subprocess.check_output(["XrdSecPROTOCOL=sss XrdSecSSSKT=/etc/ctafrontend_client_sss.keytab cta-admin --json tapepool ls"], shell=True)

cta_admin_output_json = json.loads(cta_admin_output)

#print(driveLS_dict)

for metric_list in cta_admin_output_json:
    #extracting the value of the information from the dr ls cta-admin command
    #print(drive)
    num_tapes = int(label_list['numTapes'])
    num_partial_tapes = int(label_list['numPartialTapes'])
    num_physical_files= int(label_list['numPhysicalFiles'])
    capacity_bytes= int(label_list['capacityBytes'])
    data_bytes= int(label_list['dataBytes'])
    

    #formatting to look like what parmethus wants
    extract_labels=['name','vo'] 
    produce_prom_metric('tapepool_number_of_tapes', num_tapes, label_list, labels=extract_labels)
    produce_prom_metric('tapepool_number_of_partial_tapes', num_partial_tapes, label_list,labels=extract_labels)
    produce_prom_metric('tapepool_number_of_physical_files', num_physical_files, label_list,labels=extract_labels)
    produce_prom_metric('tapepool_capacity_in_bytes', capacity_bytes, label_list,labels=extract_labels)
    produce_prom_metric('tapepool_data_in_bytes', data_bytes, label_list,labels=extract_labels)
     
