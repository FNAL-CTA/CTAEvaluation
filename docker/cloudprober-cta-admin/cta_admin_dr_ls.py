#! /usr/bin/env python3

import json
import subprocess


def produce_prom_metric(metric_name, value, drive_list, labels):
    # loop over labels to get key,value pairs
    # remove drives that we do not care about with the if not
    # import pdb; pdb.set_trace()
    # print(len(labels))
    label_list = []
    for label in labels:
        # print(label)
        label_list += [label + '="' + drive_list[label] + '"']
        # print(label_list)
    if not 'driveName="DRIVE0"' in label_list:
        print(metric_name, end='')
        print('{', ', '.join(label_list), end='')  # ,sep = ", "
        print('}', end='')
        print(f' {value}')


drLS_output = subprocess.check_output(["cta-admin --json dr ls"], shell=True)

driveLS_dict = json.loads(drLS_output)

# print(driveLS_dict)
bytes_per_session = 0.0
files_per_session = 0.0

for drive_list in driveLS_dict:
    # extracting the value of the information from the dr ls cta-admin command
    # print(drive)
    bytes_transferred = int(drive_list['bytesTransferredInSession'])
    files_transferred = int(drive_list['filesTransferredInSession'])
    session_time = int(drive_list['sessionElapsedTime'])
    if session_time == 0:
        bytes_per_session = 0
        files_per_session = 0
    elif session_time > 0:
        bytes_per_session = bytes_transferred / session_time
        files_per_session = files_transferred / session_time
    # formatting to look like what parmethus wants
    DriveLSLabels = ['vo', 'driveName', 'logicalLibrary', 'sessionId', 'tapepool']
    produce_prom_metric('drive_session_bytes', bytes_transferred, drive_list, labels=DriveLSLabels)
    produce_prom_metric('drive_session_files', files_transferred, drive_list, labels=DriveLSLabels)
    produce_prom_metric('drive_session_time', session_time, drive_list, labels=DriveLSLabels)
    produce_prom_metric('drive_session_data_rate', bytes_per_session, drive_list, labels=DriveLSLabels)
    produce_prom_metric('drive_session_file_rate', files_per_session, drive_list, labels=DriveLSLabels)
