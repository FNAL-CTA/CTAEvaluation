#! /usr/bin/env python3

import subprocess
import json


def produce_prom_metric(metric_name, metric_value, metric_input, labels):
  #loop over labels to get key,value pairs
  #remove drives that we do not care about with the if not
  #import pdb; pdb.set_trace()
  #print(len(labels))  
  #print(metric_name)
  prom_output=[]
  for label in labels:
    #print(label)
    prom_output+=[label+'="'+metric_input[label]+'"']
    #print(label_list)
  
  #if not 'driveName="DRIVE0"' in label_list:
  print(metric_name, end='')
  print('{',', '.join(prom_output),end='')#,sep = ", "
  print('}', end='')
  print(f' {metric_value}')
   

cta_admin_output = subprocess.check_output(["XrdSecPROTOCOL=sss XrdSecSSSKT=/etc/ctafrontend_client_sss.keytab cta-admin --json tapepool ls"], shell=True)

cta_admin_output_json = json.loads(cta_admin_output)

#print(driveLS_dict)

for metric_list in cta_admin_output_json:
    #extracting the value of the information from the dr ls cta-admin command
    #print(drive)
    num_tapes = int(metric_list['numTapes'])
    num_partial_tapes = int(metric_list['numPartialTapes'])
    num_physical_files= int(metric_list['numPhysicalFiles'])
    capacity_bytes= int(metric_list['capacityBytes'])
    data_bytes= int(metric_list['dataBytes'])
    

    #formatting to look like what parmethus wants
    extract_labels=['name','vo'] 
    produce_prom_metric('tapepool_number_of_tapes', num_tapes, metric_list, labels=extract_labels)
    produce_prom_metric('tapepool_number_of_partial_tapes', num_partial_tapes, metric_list,labels=extract_labels)
    produce_prom_metric('tapepool_number_of_physical_files', num_physical_files, metric_list,labels=extract_labels)
    produce_prom_metric('tapepool_capacity_in_bytes', capacity_bytes, metric_list,labels=extract_labels)
    produce_prom_metric('tapepool_data_in_bytes', data_bytes, metric_list,labels=extract_labels)
     
