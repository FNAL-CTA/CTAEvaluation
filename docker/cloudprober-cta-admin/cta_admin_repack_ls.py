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
        #print(label_list)

    print(metric_name, end='')
    print('{', ', '.join(label_list), end='')  # ,sep = ", "
    print('}', end='')
    print(f' {metric_value}')


cta_admin_output = subprocess.check_output(["cta-admin --json repack ls"], shell=True)

cta_admin_output_json = json.loads(cta_admin_output)

# newly added code, still in progress
retrieved_files = 0
archived_files = 0
total_files_to_retrieve = 0
total_files_to_archive = 0
failed_retrieve_files = 0
failed_archive_files = 0
vid = 0

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
        vid = metric["vid"]

    #print(f"The total files to retrieve is {total_files_to_retrieve}")
    #print(f"The total files to archive is {total_files_to_archive}")
    #print(f"The retrieved files are {retrieved_files}")
    #print(f"The archived files are {archived_files}")
    #print(f"The failed to retrieve files are {failed_retrieve_files}")
    #print(f"The failed to archive files are {failed_archive_files}")
    #print(f"The vid is {vid}")

    # formatting to look like what prometheus wants
    produce_prom_metric('repack_retrieved_files', retrieved_files, None, labels=[])
    produce_prom_metric('repack_archived_files', archived_files, None, labels=[])
    produce_prom_metric('repack_total_files_to_retrieve', total_files_to_retrieve, None, labels=[])
    produce_prom_metric('repack_total_files_to_archive', total_files_to_archive, None, labels=[])
    produce_prom_metric('repack_failed_retrieve_files', failed_retrieve_files, None, labels=[])
    produce_prom_metric('repack_failed_archive_files', failed_archive_files, None, labels=[])
    produce_prom_metric('repack_vid', vid, None, labels=[])

