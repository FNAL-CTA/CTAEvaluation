#! /usr/bin/env python3

import json
import subprocess


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


cta_admin_output = subprocess.check_output(["cta-admin --json fr ls -S"], shell=True)

cta_admin_output_json = json.loads(cta_admin_output)

archive_files = 0
archive_bytes = 0
retrieve_files = 0
retrieve_bytes = 0

for metric_list in cta_admin_output_json:
    if metric_list['requestType'] == 'ARCHIVE_REQUEST':
        archive_files = int(metric_list['totalFiles'])
        archive_bytes = int(metric_list['totalSize'])
    if metric_list['requestType'] == 'RETRIEVE_REQUEST':
        retrieve_files = int(metric_list['totalFiles'])
        retrieve_bytes = int(metric_list['totalSize'])

# formatting to look like what prometheus wants
produce_prom_metric('failedrequests_retrieve_files', retrieve_files, None, labels=[])
produce_prom_metric('failedrequests_retrieve_bytes', retrieve_bytes, None, labels=[])
produce_prom_metric('failedrequests_archive_files', archive_files, None, labels=[])
produce_prom_metric('failedrequests_archive_bytes', archive_bytes, None, labels=[])
