#!/usr/bin/env python3

import datetime
import random
import subprocess
import time

GB_PER_DAY = 1*1000
AVG_FILE_SIZE_GB = 3.7
SLEEP_AFTER_EVICT = 300
CYCLE_HOURS = 1
SCAN_DIRECTORIES = [
    '/eos//ctaeos/ctacms/pnfs/fs/usr/cms/WAX/11/store/mc',
    '/eos//ctaeos/ctacms/pnfs/fs/usr/cms/WAX/11/store/data',
]

files_per_cycle = int(GB_PER_DAY / 24 / AVG_FILE_SIZE_GB * CYCLE_HOURS)


def sleep_until_next_hour(hours=CYCLE_HOURS):
    delta = datetime.timedelta(hours=hours)
    now = datetime.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=0, minute=1)
    wait_seconds = (next_hour - now).seconds
    print(f'Sleeping {wait_seconds} seconds or {wait_seconds / 60:.1f} minutes')
    time.sleep(wait_seconds)


def collect_files(directory, file_list=None):
    result = subprocess.run(['env', 'XrdSecPROTOCOL=sss', 'XrdSecSSSKT=/etc/cta/eos.sss.keytab',
                             '/opt/eos/xrootd/bin/xrdfs', 'root://cmscta-eosmgm-01.fnal.gov', 'ls', '-R', directory],
                            stdout=subprocess.PIPE)
    root_files = [f for f in result.stdout.splitlines() if f.endswith(b'.root')]
    file_list.extend(root_files)
    return


print(f'Will evict and stage {files_per_cycle} files per {CYCLE_HOURS} hour cycle')

while True:

    file_list = []
    for directory in SCAN_DIRECTORIES:
        collect_files(directory=directory, file_list=file_list)

    print(f'Selecting {files_per_cycle} files from list of {len(file_list)}. Evicting files.')
    files_to_stage = random.sample(file_list, k=files_per_cycle)

    for eos_file in files_to_stage:
        result = subprocess.run(['env', 'XrdSecPROTOCOL=sss', 'XrdSecSSSKT=/etc/cta/eos.sss.keytab',
                                 '/opt/eos/xrootd/bin/xrdfs', 'root://cmscta-eosmgm-01.fnal.gov', 'prepare', '-e',
                                 eos_file],
                                stdout=subprocess.PIPE)
    print(f'Sleeping for {SLEEP_AFTER_EVICT} seconds.')
    time.sleep(SLEEP_AFTER_EVICT)
    for eos_file in files_to_stage:
        print(f'Staging file {eos_file}')
        result = subprocess.run(['env', 'XrdSecPROTOCOL=sss', 'XrdSecSSSKT=/etc/cta/eos.sss.keytab',
                                 '/opt/eos/xrootd/bin/xrdfs', 'root://cmscta-eosmgm-01.fnal.gov', 'prepare', '-s',
                                 eos_file],
                                stdout=subprocess.PIPE)

    sleep_until_next_hour(hours=CYCLE_HOURS)
