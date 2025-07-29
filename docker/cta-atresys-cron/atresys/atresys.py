#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import argparse

from datetime import datetime

DEFAULT_CONFIG_PATH = "/etc/cta-ops/cta-ops-config.yaml"
CONFIG = lambda x: f"-C|{DEFAULT_CONFIG_PATH}" if x is None else f"-C|{x}"
VERBOSE = lambda x: "-V" if x else None
JSON = lambda x: "-j" if x else None

def print_override(*args, **kwargs):
    """
    Print function that overrides the default print to handle verbose and json output.
    """
    global verbose
    if verbose:
        message = "[VERBOSE] "
        if kwargs.get('error', False):
            sys.stderr.write("\n")
            message = "[ERROR] "
        for arg in args:
            if isinstance(arg, str):
                arg = arg.strip()
            lines = arg.splitlines()
            if lines and len(lines) > 0:
                for line in lines:
                    sys.stderr.write(f"{message}{line}\n")

print = print_override


COMMANDS = {
    "scan": "cta-ops-repack-0-scan",
    "prepare": "cta-ops-repack-1-prepare",
    "start": "cta-ops-repack-2-start",
    "end": "cta-ops-repack-3-end",
    "quarantine": "cta-ops-repack-4-quarantine",
    "reclaim": "cta-ops-repack-5-reclaim",
    "finish": "cta-ops-repack-6-finish",
}
SCAN_OUT = lambda res: res.split() if res else []

OUTPUT_FMT = {
    "scan": SCAN_OUT
}


def base_command(cmd, args):
    """
    Returns the base command for atresys.
    """
    full_command = []
    global operation
    operation = str(cmd)
    cmd = COMMANDS.get(cmd)
    if not cmd:
        raise ValueError(f"Unknown command: {cmd}")
    full_command.append(cmd)
    for attr in ["config", "verbose", "json"]:
        if hasattr(args, attr) and globals().get(attr.upper(), None) is not None:
            value = globals().get(attr.upper())(getattr(args, attr))
            if value is not None:
                full_command += value.split("|")
    return full_command

def load_cmd():
    """
    Loads the options for all possible script arguments
    """
    parser = argparse.ArgumentParser(
        description="Atresys is a tool for managing CTA repacks and other operations.",
    )
    parser.add_argument(
        "command",
        type=str,
        help="The command to run. Choose from: %s" % ", ".join(list(COMMANDS.keys())),
    )
 
    # Settings
    settings_group = parser.add_argument_group("settings", "Configure how this script runs")
    settings_group.add_argument(
        "-C",
        "--config",
        default="/etc/cta-ops/cta-ops-config.yaml",
        help="The path to the config file (default: /etc/cta-ops/cta-ops-config.yaml)"
    )
    settings_group.add_argument(
        "-V", "--verbose", action="store_true", help="Generate more detailed logs"
    )
    settings_group.add_argument(
        "-j", "--json", action="store_true", help="Output in JSON format"
    )
    
    # Parse the arguments & generate the full command
    args, extra_args = parser.parse_known_args()
    base_cmd = base_command(args.command, args)
    full_cmd = " ".join(base_cmd + extra_args)
    
    # Set global variables for verbose and json
    global verbose, json
    verbose = args.verbose
    json = args.json
    
    return full_cmd
    

def run_command(command):
    """
    Run a shell command and return the output.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error running command: '{command}'\n\n{e.stderr.decode('utf-8')} {e.output}", error=True)
        raise e

def main():
    global verbose, operation
    
    # start the timer
    metrics = {}
    started = datetime.now()
    metrics["started"] = started.isoformat()
    # List all files in the current directory
   
    full_cmd = load_cmd()
    metrics["operation"] = operation
    metrics["full_cmd"] = full_cmd
    try:
        stdout, stderr = run_command(full_cmd)
        metrics["status"] = "success"
        if stdout:
            metrics["output"] = stdout.strip()
            for line in stdout.splitlines():
                print(f"[stdout]: {line}")
        if stderr and verbose:
            for line in stderr.splitlines():
                print(f"[stderr]: {line}")
        metrics["return_code"] = 0
    except subprocess.CalledProcessError as e:
        metrics["status"] = "failure"
        if e.stderr:
            metrics["error_msg"] = e.stderr.decode('utf-8').splitlines()
        metrics["return_code"] = e.returncode

        
    
    
    # calculate the duration of the operation
    finished = datetime.now()
    metrics["finished"] = finished.isoformat()
    metrics["duration"] = (finished - started).total_seconds()
    
    if metrics["status"] == "success":
        metrics['output'] = OUTPUT_FMT[metrics["operation"]](metrics['output'])
    
    if operation == "scan":
        global DEFAULT_CONFIG_PATH
        from tools.database import Database
        db = Database(DEFAULT_CONFIG_PATH)
        db.add_scanned_objects(metrics)
    import json
    sys.stdout.write(json.dumps(metrics, indent=4) + "\n")
    
    
    

    
    

    
if "__main__" == "__main__":
    main()