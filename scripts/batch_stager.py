#! /usr/bin/env python3

from __future__ import print_function

import csv
import random
import json
import os
import subprocess
import time

TAPES = 2
BATCHES = 2
FILES = 4
SLEEP = 40
CSV_FILES = ['VR5775M8.csv', 'VR5776M8.csv']

eos_files = []

for csv_filename in CSV_FILES[:TAPES]:
    with open(f'../data/{csv_filename}') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            eos_files.append('/eos/ctaeos/cta' + row['pnfs_path'])

random.shuffle(eos_files)

for _i in range(BATCHES):
    for _j in range(FILES):
        eos_file = eos_files.pop()
        print(eos_file)
        result = subprocess.run(['env', 'KRB5_CONFIG=/etc/krb5.cta.conf', 'KRB5CCNAME=/tmp/krb5cache', 'xrdfs',
                                 'storagedev201.fnal.gov', 'prepare', '-s', eos_file],
                                stdout=subprocess.PIPE)
        result = subprocess.run(['env', 'KRB5_CONFIG=/etc/krb5.cta.conf', 'KRB5CCNAME=/tmp/krb5cache', 'xrdfs',
                                 'storagedev201.fnal.gov', 'prepare', '-e', eos_file],
                                stdout=subprocess.PIPE)
    print('')
    time.sleep(SLEEP)
