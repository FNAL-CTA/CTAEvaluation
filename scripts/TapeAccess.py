#! /usr/bin/env python3
import subprocess


class Drive:
    def __init__(self, device: str):
        self.device = device

    def write_data_to_tape(self, data: bytes,  block_size: int = 262144) -> int:
        with open('/tmp/test', 'wb') as test_file:
            test_file.write(data)
        result = self.copy_file_to_tape('/tmp/test', block_size=block_size)
        return result

    def make_tape_mark(self) -> int:
        print(f'TapeAccess: Making tape mark on {self.device}')
        result = subprocess.run(['mt', '-f', self.device, 'eof'], stdout=subprocess.PIPE)
        return result.returncode

    def copy_file_to_tape(self, file_name: str, block_size: int = 262144):
        print(f'TapeAccess: Copying file {file_name} to {self.device} with dd')
        result = subprocess.run(['dd', f'if={file_name}', f'of={self.device}', f'bs={block_size}'],
                                stdout=subprocess.PIPE)
        return result.returncode

    def rewind_tape(self):
        print(f'TapeAccess: Rewinding {self.device}')
        result = subprocess.run(['mt', '-f', f'{self.device}', 'rewind'], stdout=subprocess.PIPE)
        return result.returncode


class Changer:
    def __init__(self, changer_device: str = '/dev/smc'):
        self.changer_device = changer_device

    def load_tape(self, tape: int = 0, drive: int = 0):
        print(f'TapeAccess: loading {tape} into drive {drive}')
        result = subprocess.run(['mtx', '-f', self.changer_device, 'load', str(tape), str(drive)],
                                stdout=subprocess.PIPE)
        return result.returncode

    def unload_tape(self, tape: int = 0, drive: int = 0):
        print(f'TapeAccess: unloading {tape} from drive {drive}')
        result = subprocess.run(['mtx', '-f', self.changer_device, 'unload', str(tape), str(drive)],
                                stdout=subprocess.PIPE)
        return result.returncode
