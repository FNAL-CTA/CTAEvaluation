#! /usr/bin/env python3

def produce_prom_metric(metric_name, metric_value, list_input, labels):
    # loop over labels to get key,value pairs
    label_list = [] 
    for label in labels:
        label_list += [label + '="' + list_input[label] + '"']

    print(metric_name, end='')
    print('{', ', '.join(label_list), end='')  # ,sep = ", "
    print('}', end='')
    print(f' {metric_value}')
