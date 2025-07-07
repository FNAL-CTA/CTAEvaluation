#! /usr/bin/env python3

import json
import subprocess
from common import produce_prom_metric

DriveLSLabels = ['vo', 'driveName', 'logicalLibrary', 'sessionId', 'tapepool', 'mountType', 'host']
DRIVE_CODE_LABELS = ['vo', 'driveName', 'logicalLibrary', 'host', 'mountType', 'driveStatus', 'driveState']

OTHER_STATUS = ['PROBING', 'STARTING', 'MOUNTING', 'UNLOADING', 'UNMOUNTING', 'DRAININGTODISK', 'CLEANINGUP',
                'SHUTDOWN', 'UNKNOWN']
WRITING_TYPE = ["ARCHIVE_FOR_USER", "ARCHIVE_FOR_REPACK", "ARCHIVE_ALL_TYPES"]


drLS_output = subprocess.check_output(["cta-admin", "--json", "dr", "ls"])

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


def get_drive_code(drive_status, mount_type):
    state_matrix = {'UP': {'NO_MOUNT': 'Free'},
                    'TRANSFERRING': {'ARCHIVE_FOR_USER': 'User Archiving', "ARCHIVE_FOR_REPACK": 'Repack Archiving',
                                     "ARCHIVE_ALL_TYPES": 'Archiving other',
                                     "RETRIEVE": 'Retrieving'}
                    }
    if drive_status not in state_matrix.keys():
        drive_code = drive_status
    else:
        if mount_type in state_matrix[drive_status].keys():
            drive_code = state_matrix[drive_status][mount_type]
        else:
            drive_code = drive_status + "-" + mount_type

    """
    drive_code: int = 99
    other_status = {'UNKNOWN': 1, 'DOWN': 2, 'SHUTDOWN': 3, 'PROBING': 11, 'STARTING': 12, 'MOUNTING': 13,
                    'UNLOADING': 14, 'UNMOUNTING': 15, 'DRAININGTODISK': 16, 'CLEANINGUP': 17}
    up_status = {'NO_MOUNT': 40}
    transfer_status = {"ARCHIVE_FOR_USER": 21, "ARCHIVE_FOR_REPACK": 22, "ARCHIVE_ALL_TYPES": 23,
                       "RETRIEVE": 31}
    other_mount_type = 59
    other_up_mount = 49

    if drive_status in other_status.keys():
        drive_code = other_status[drive_status]
    elif drive_status == 'UP':
        drive_code = other_up_mount
        if mount_type in up_status.keys():
            drive_code = up_status[mount_type]
    elif drive_status == 'TRANSFERRING':
        drive_code = other_mount_type
        if mount_type in transfer_status.keys():
            drive_code = transfer_status[mount_type]
"""
    return drive_code


for drive_list in driveLS_dict:
    # extracting the value of the information from the dr ls cta-admin command
    # print(drive)
    bytes_transferred = int(drive_list['bytesTransferredInSession'])
    files_transferred = int(drive_list['filesTransferredInSession'])
    session_time = int(drive_list['sessionElapsedTime'])
    drive_status = drive_list['driveStatus']
    mount_type = drive_list['mountType']

    # Produce the list of drive status and mount type for each drive
    drive_code = get_drive_code(drive_status, mount_type)
    # produce_prom_metric('drive_code', drive_code, drive_list, labels=DRIVE_CODE_LABELS)
    drive_list.update({'driveState' : drive_code})
    produce_prom_metric('drive_state', 1, drive_list, labels=DRIVE_CODE_LABELS)

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
