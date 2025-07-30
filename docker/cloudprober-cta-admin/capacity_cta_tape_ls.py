#! /usr/bin/env python3

import json
import subprocess
from common import produce_prom_metric

extract_labels = ['vo', 'tapepool', 'vid', 'logicalLibrary', 'full']

cta_admin_output = subprocess.check_output(["cta-admin", "--json", "tape", "ls", "--all"])

cta_admin_output_json = json.loads(cta_admin_output)

available_space_on_tape = 0
partial_tapes_per_library_count = {}
enstore_partial_tapes_per_library_count = {}
available_space_per_library = {}
occupied_space_per_library = {}
fully_filled_tapes_per_library_count = {}

for metric in cta_admin_output_json:
    # extracting the value of the information from the tape ls cta-admin command
    capacity = int(metric.get('capacity', -1))
    occupancy = int(metric.get('occupancy', -1))
    tapepool = str(metric.get('tapepool', 'unknown'))
    logical_library = str(metric.get('logicalLibrary', 'unknown'))
    vid = str(metric.get('vid', 'unknown'))
    vo = str(metric.get('vo', 'unknown'))
    full = str(metric.get('full', 'unknown'))

    # calculating the available space in each tape
    available_space_on_tape = capacity - occupancy

    # counting total number of partially filled Enstore tapes per library depending on individual tape capacity
    if 0 < occupancy < (0.20*capacity): 
        if full == 'True':
            if logical_library not in enstore_partial_tapes_per_library_count:
                enstore_partial_tapes_per_library_count[logical_library] = 0
            enstore_partial_tapes_per_library_count[logical_library] += 1

    # adding number of bytes per library for total available space per library (tapes not from Enstore)
    if full == 'False':
        if logical_library not in available_space_per_library:
            # initializes value for the library if it does not yet exist in dictionary
            available_space_per_library[logical_library] = 0
        available_space_per_library[logical_library] += available_space_on_tape

    # adding tape occupancy for total occupied bytes per library
    if logical_library not in occupied_space_per_library:
        occupied_space_per_library[logical_library] = 0
    occupied_space_per_library[logical_library] += occupancy

    # number of fully filled tapes per library
    if occupancy >= (0.95*capacity):
        if logical_library not in fully_filled_tapes_per_library_count:
            fully_filled_tapes_per_library_count[logical_library] = 0
        fully_filled_tapes_per_library_count[logical_library] += 1
    
    # counting total number of partially filled tapes per library (0 < occupancy < (0.95*capacity))
    else:
        if logical_library not in partial_tapes_per_library_count:
            # initializes value for the library if the library does not yet exist in dictionary
            partial_tapes_per_library_count[logical_library] = 0
        partial_tapes_per_library_count[logical_library] += 1 

    labels_dict = {"vo": vo, "tapepool": tapepool, "vid": vid, "logical_library": logical_library, "full": full}

    # optional prometheus per-tape metrics
    #produce_prom_metric('tape_capacity', capacity, labels_dict, labels=extract_labels)
    #produce_prom_metric('tape_occupancy', occupancy, labels_dict, labels=extract_labels)
    #produce_prom_metric('tape_available_space', available_space_on_tape, labels_dict, labels=extract_labels)

# formatting for prometheus, returning total available space per library in bytes (excluding enstore tapes)
for logical_library, total_available_space in available_space_per_library.items():
    produce_prom_metric('tape_library_total_available_space', total_available_space, {"logical_library": logical_library}, labels=["logical_library"])

# number of partially filled tapes per library
for logical_library, partially_filled_tapes in partial_tapes_per_library_count.items():
    produce_prom_metric('total_tapes_partially_filled', partially_filled_tapes, {"logical_library": logical_library}, labels=["logical_library"])

# number of enstore partially filled tapes per library
for logical_library, enstore_partially_filled_tapes in enstore_partial_tapes_per_library_count.items():
    produce_prom_metric('enstore_total_tapes_partially_filled', enstore_partially_filled_tapes, {"logical_library": logical_library}, labels=["logical_library"])

# occupied space per library in bytes
for logical_library, occupied_space in occupied_space_per_library.items():
    produce_prom_metric('total_occupied_space_per_library', occupied_space, {"logical_library": logical_library}, labels=["logical_library"])

# number of fully filled tapes per library
for logical_library, fully_filled_tapes in fully_filled_tapes_per_library_count.items():
    produce_prom_metric('total_fully_filled_tapes', fully_filled_tapes, {"logical_library": logical_library}, labels=["logical_library"])
