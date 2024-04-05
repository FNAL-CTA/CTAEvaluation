#!/usr/bin/env python3

import datetime
import multiprocessing
import os
import random
import socket
import subprocess
import sys
import time
import uuid

GB_PER_DAY = 60 * 1000
AVG_FILE_SIZE_GB = 3.7
SLEEP_AFTER_EVICT = 60
CYCLE_HOURS = 1
SLICES = 4
STOP_FILE = "/tmp/STOP"

UUID = str(uuid.uuid4())
KRB5CCNAME = f"/tmp/krb5cc_root.migration-{UUID}"
os.environ["KRB5CCNAME"] = KRB5CCNAME

SCAN_DIRECTORIES = (
    '/pnfs/store/mc',
    '/pnfs/store/data',
)

files_per_cycle = int(GB_PER_DAY / 24 / AVG_FILE_SIZE_GB * CYCLE_HOURS / SLICES) + 1


def get_pnfsid(path):
    pnfsid = None
    dn = os.path.dirname(path)
    fn = os.path.basename(path)
    with open(f"{dn}/.(id)({fn})", "r") as fh:
        pnfsid = fh.readlines()[0].strip()
    return pnfsid


def execute_command(cmd):
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    output, errors = p.communicate()
    rc = p.returncode
    return rc, output, errors


class KinitWorker(multiprocessing.Process):

    HOSTNAME = socket.gethostname()

    def __init__(self):
        super(KinitWorker, self).__init__()
        self.stop = False
        self.lock = multiprocessing.Lock()

    def kinit(self):
        cmd = f"/usr/bin/kinit -k host/{KinitWorker.HOSTNAME}"
        execute_command(cmd)

    def run(self):
        while not self.stop:
            with self.lock:
                self.kinit()
                time.sleep(14400)


def sleep_until_next_hour(hours=CYCLE_HOURS):
    delta = datetime.timedelta(hours=hours)
    now = datetime.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=0, minute=1)
    wait_seconds = (next_hour - now).seconds
    print(f'Sleeping {wait_seconds} seconds or {wait_seconds / 60:.1f} minutes')
    time.sleep(wait_seconds)


def collect_files(directory, file_list=None):
    # we need mounted PNFS and find all files
    # that are older than 1 day just in case we don't expunge
    # files that are not on tape yet
    result = subprocess.run(['find', directory,
                             '-type', 'f',
                             '-mtime', '+1' ],
                            stdout=subprocess.PIPE)
    root_files = [get_pnfsid(f.decode("utf-8")) for f in result.stdout.splitlines() if f.endswith(b'.root')]
    file_list.extend(root_files)
    return


print(f'Will evict and stage {SLICES} slices of {files_per_cycle} ({SLICES*files_per_cycle} total) files per {CYCLE_HOURS} hour cycle')

kinitWorker = KinitWorker()
kinitWorker.start()

try:
    while True:

        if os.path.exists(STOP_FILE):
            break

        file_list = []
        for directory in SCAN_DIRECTORIES:
            collect_files(directory=directory, file_list=file_list)

        print(f'Selecting {files_per_cycle} files from list of {len(file_list)}. Evicting files.')
        files_to_stage = []
        for _ in range(SLICES):
            first_file = random.randint(0, len(file_list) - 1 - files_per_cycle)
            files_to_stage.extend(file_list[first_file:first_file + files_per_cycle])

        new_list = []
        for eos_file in files_to_stage:
            cmd = f"ssh -p 22224 admin@cmstnvm1 \"\sl {eos_file} rep rm {eos_file}\""
            rc, out, err = execute_command(cmd)
            out = out.decode("utf-8")
            if out.find("File is not removable; use -force to override") == -1:
                new_list.append(eos_file)
            else:
                print(f"Skipping file {eos_file}")

        print(f'Sleeping for {SLEEP_AFTER_EVICT} seconds.')
        time.sleep(SLEEP_AFTER_EVICT)
        for eos_file in new_list:
            print(f'Staging file {eos_file}')
            # dccp is provided by dcap package
            result = subprocess.run(['dccp', '-P', f'pnfs://cmstnvm1:22125/{eos_file}'],
                                    stdout=subprocess.PIPE)

        sleep_until_next_hour(hours=CYCLE_HOURS)
except:
    raise
finally:
    kinitWorker.stop = True
    kinitWorker.terminate()
    try:
        os.unlink(STOP_FILE)
    except:
        pass
