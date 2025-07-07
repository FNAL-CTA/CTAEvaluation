#! /usr/bin/env python3
import json
import subprocess

extract_labels = ['vo', 'tapepool', 'vid', 'status']

def produce_prom_metric(metric_name, metric_value, list_input, labels):
    # loop over labels to get key,value pairs
    # print(len(labels))
    # print(metric_name)
    label_list = []
    for label in labels:
        # print(label)
        label_list += [label + '="' + list_input[label] + '"']
        #print(label_list)

    print(metric_name, end='')
    print('{', ', '.join(label_list), end='')  # ,sep = ", "
    print('}', end='')
    print(f' {metric_value}')


cta_admin_output = subprocess.check_output(["cta-admin", "--json", "repack", "ls"])

cta_admin_output_json = json.loads(cta_admin_output)

retrieved_files = 0
archived_files = 0
total_files_to_retrieve = 0
total_files_to_archive = 0
failed_retrieve_files = 0
failed_archive_files = 0
vid = ""
tapepool = ""
status = ""

for metric in cta_admin_output_json:
    if "totalFilesToRetrieve" in metric:
        total_files_to_retrieve = int(metric["totalFilesToRetrieve"])
    if "totalFilesToArchive" in metric:
        total_files_to_archive = int(metric["totalFilesToArchive"])
    if "retrievedFiles" in metric:
        retrieved_files = int(metric["retrievedFiles"])
    if "archivedFiles" in metric:
        archived_files = int(metric["archivedFiles"])
    if "failedToRetrieveFiles" in metric:
        failed_retrieve_files = int(metric["failedToRetrieveFiles"])
    if "failedToArchiveFiles" in metric:
        failed_archive_files = int(metric["failedToArchiveFiles"])
    if "vid" in metric:
        vid = str(metric["vid"])
    if "tapepool" in metric:
        tapepool = str(metric["tapepool"])
    if "status" in metric:
        status = str(metric["status"])

    # get vo for the vid
    cta_admin_output_tape_ls_json = json.loads(subprocess.check_output(["cta-admin", "--json", "tape", "ls", "-v", vid]))

    vo = ""
    for tape in cta_admin_output_tape_ls_json:
        if "vo" in tape:
            vo = str(tape["vo"])
            break

    labels_dict = {"vo": vo, "tapepool": tapepool, "vid": vid, "status": status}

    produce_prom_metric('repack_retrieved_files', retrieved_files, labels_dict, labels=extract_labels)
    produce_prom_metric('repack_archived_files', archived_files, labels_dict, labels=extract_labels)
    produce_prom_metric('repack_total_files_to_retrieve', total_files_to_retrieve, labels_dict, labels=extract_labels)
    produce_prom_metric('repack_total_files_to_archive', total_files_to_archive, labels_dict, labels=extract_labels)
    produce_prom_metric('repack_failed_retrieve_files', failed_retrieve_files, labels_dict, labels=extract_labels)
    produce_prom_metric('repack_failed_archive_files', failed_archive_files, labels_dict, labels=extract_labels)
