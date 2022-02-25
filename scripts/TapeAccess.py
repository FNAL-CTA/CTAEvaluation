#! /usr/bin/env python3
import subprocess


def write_data_to_tape(device: str, data: bytes) -> int:
    with open('/tmp/test', 'wb') as test_file:
        test_file.write(data)
    result = copy_file_to_tape(device, '/tmp/test')
    return result


def make_tape_mark(device: str) -> int:
    print(f'TapeAccess: Making tape mark on {device}')
    result = subprocess.run(['mt', '-f', device, 'eof'], stdout=subprocess.PIPE)
    return result.returncode


def load_tape(changer_device: str = '/dev/smc', tape: int = 0, drive: int = 0):
    print(f'TapeAccess: loading {tape} into drive {drive}')
    result = subprocess.run(['mtx', '-f', changer_device, 'load', str(tape), str(drive)], stdout=subprocess.PIPE)
    return result.returncode


def unload_tape(changer_device: str = '/dev/smc', tape: int = 0, drive: int = 0):
    print(f'TapeAccess: unloading {tape} from drive {drive}')
    result = subprocess.run(['mtx', '-f', changer_device, 'unload', str(tape), str(drive)], stdout=subprocess.PIPE)
    return result.returncode


def copy_file_to_tape(device: str, file_name: str, block_size: int = 262144, count: int = 1):
    print(f'TapeAccess: Copying file {file_name} to {device} with dd')
    result = subprocess.run(['dd', f'if={file_name}', f'if={device}', f'bs={block_size}', f'count={count}'],
                            stdout=subprocess.PIPE)
    return result.returncode
