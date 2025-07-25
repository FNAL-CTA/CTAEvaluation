#! /usr/bin/env python3

import json
import subprocess

tapeLS_output = subprocess.check_output(["cta-admin", "--json", "tape", "ls", "--all"])

tapeLS_dict = json.loads(tapeLS_output)

n_enstore = 0
n_cta = 0
n_enstore_large = 0
n_unknown = 0

for tape in tapeLS_dict:
    # extracting the value of the information from the tape ls cta-admin command
    label_format = tape.get('labelFormat', 'Unknown')

    if label_format == 'CTA':
        n_cta += 1
    elif label_format == 'Enstore':
        n_enstore += 1
    elif label_format == 'EnstoreLarge':
        n_enstore_large += 1
    else:
        n_unknown += 1

# FIXME: May want to collect and display these by logical library in the future
print('tape_info{label_format="CTA"}', n_cta)
print('tape_info{label_format="Enstore"}', n_enstore)
print('tape_info{label_format="EnstoreLarge"}', n_enstore_large)
print('tape_info{label_format="Unknown"}', n_unknown)
