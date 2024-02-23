#! /usr/bin/env python3

import json
import subprocess

extract_labels = ['name', 'vo']


def produce_prom_metric(metric_name, metric_value, list_input, labels):
    # loop over labels to get key,value pairs
    # print(len(labels))
    # print(metric_name)
    label_list = []
    for label in labels:
        # print(label)
        label_list += [label + '="' + list_input[label] + '"']
        # print(label_list)

    print(metric_name, end='')
    print('{', ', '.join(label_list), end='')  # ,sep = ", "
    print('}', end='')
    print(f' {metric_value}')


cta_admin_output = subprocess.check_output(["cta-admin --json tapepool ls"], shell=True)

cta_admin_output_json = json.loads(cta_admin_output)

# print(driveLS_dict)

for metric_list in cta_admin_output_json:
    # extracting the value of the information from the tapepool ls cta-admin command
    num_tapes = int(metric_list['numTapes'])
    num_partial_tapes = int(metric_list['numPartialTapes'])
    num_physical_files = int(metric_list['numPhysicalFiles'])
    capacity_bytes = int(metric_list['capacityBytes'])
    data_bytes = int(metric_list['dataBytes'])

    # formatting to look like what prometheus wants
    produce_prom_metric('tapepool_number_of_tapes', num_tapes, metric_list, labels=extract_labels)
    produce_prom_metric('tapepool_number_of_partial_tapes', num_partial_tapes, metric_list, labels=extract_labels)
    produce_prom_metric('tapepool_number_of_physical_files', num_physical_files, metric_list, labels=extract_labels)
    produce_prom_metric('tapepool_capacity_in_bytes', capacity_bytes, metric_list, labels=extract_labels)
    produce_prom_metric('tapepool_data_in_bytes', data_bytes, metric_list, labels=extract_labels)
