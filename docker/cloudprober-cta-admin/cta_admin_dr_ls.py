#! /usr/bin/env python3

import json
import subprocess

DriveLSLabels = ['vo', 'driveName', 'logicalLibrary', 'sessionId', 'tapepool', 'mountType', 'host']

OTHER_STATUS = ['PROBING', 'STARTING', 'MOUNTING', 'UNLOADING', 'UNMOUNTING', 'DRAININGTODISK', 'CLEANINGUP',
                'SHUTDOWN', 'UNKNOWN']
WRITING_TYPE = ["ARCHIVE_FOR_USER", "ARCHIVE_FOR_REPACK", "ARCHIVE_ALL_TYPES"]


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
    # FIXME: This logic belongs in the outer script, not here.
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

n_down = 0
n_idle = 0
n_writing = 0
n_reading = 0
n_repack = 0
n_other = 0

for drive_list in driveLS_dict:
    # extracting the value of the information from the dr ls cta-admin command
    # print(drive)
    bytes_transferred = int(drive_list['bytesTransferredInSession'])
    files_transferred = int(drive_list['filesTransferredInSession'])
    session_time = int(drive_list['sessionElapsedTime'])
    drive_status = drive_list['driveStatus']
    mount_type = drive_list['mountType']

    if session_time == 0:
        bytes_per_session = 0
        files_per_session = 0
    elif session_time > 0:
        bytes_per_session = bytes_transferred / session_time
        files_per_session = files_transferred / session_time
    # formatting to look like what prometheus wants

    produce_prom_metric('drive_session_bytes', bytes_transferred, drive_list, labels=DriveLSLabels)
    produce_prom_metric('drive_session_files', files_transferred, drive_list, labels=DriveLSLabels)
    produce_prom_metric('drive_session_time', session_time, drive_list, labels=DriveLSLabels)
    produce_prom_metric('drive_session_data_rate', bytes_per_session, drive_list, labels=DriveLSLabels)
    produce_prom_metric('drive_session_file_rate', files_per_session, drive_list, labels=DriveLSLabels)

    if drive_status in OTHER_STATUS:
        n_other += 1
    elif drive_status == 'TRANSFERRING':
        if mount_type == 'RETRIEVE':
            n_reading += 1
        if mount_type in WRITING_TYPE:
            n_writing += 1
    elif drive_status == 'DOWN':
        n_down += 1
    elif drive_status == 'UP' and mount_type == "NO_MOUNT":
        n_idle += 1

# FIXME: May want to collect and display these by logical library in the future
print('drive_status{status="Down"}', n_down)
print('drive_status{status="Idle"}', n_idle)
print('drive_status{status="Writing"}', n_writing)
print('drive_status{status="Reading"}', n_reading)
print('drive_status{status="Other"}', n_other)
