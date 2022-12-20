import json
import subprocess


class EosInfo:
    def __init__(self, server: str):
        self.eos_ids = {}
        self.server = server
        self.eos_url = f"root://{self.server}"

    def id_for_file(self, path: str) -> int:
        """
        Cache and retrieve the IDs of a path

        :param path: The full path of the file or directory to get the ID for
        :return: the ID number of the path
        """
        if path in self.eos_ids:
            return self.eos_ids[path]
        result = subprocess.run(['eos', '--json', self.eos_url, 'info', path], stdout=subprocess.PIPE)
        eos_info = json.loads(result.stdout.decode('utf-8'))
        try:
            self.eos_ids[path] = int(eos_info['id'])
        except KeyError:
            return None
        except ValueError:
            raise RuntimeError('Could not determine EOS file ID')
        return self.eos_ids[path]

    def make_eos_file(self, path: str, size: int, archive_file_id: int, storage_class: str):
        """
        Make a file on EOS with the right attributes but with no data. Executes:

        eos file touch -n [path] [size]
        eos file layout [path] -type 00100012 # single copy and adler checksum
        eos file tag [path] +65535 # tag the file to be on tape
        eos attr set sys.archive.file_id=archive_file_id [path]
        eos attr set sys.archive.storage_class=sc [path]
        """

        result = subprocess.run(['eos', self.eos_url, 'file', 'touch', '-n', path, size], stdout=subprocess.PIPE)
        if result:
            raise RuntimeError
        result = subprocess.run(['eos', self.eos_url, 'file', 'layout', '-n', path, '-type', '00100012'],
                                stdout=subprocess.PIPE)
        if result:
            raise RuntimeError
        result = subprocess.run(['eos', self.eos_url, 'file', 'tag', path, '+65535'], stdout=subprocess.PIPE)
        if result:
            raise RuntimeError
        result = subprocess.run(['eos', self.eos_url, 'attr', 'set', f'sys.archive.file_id={archive_file_id}', path],
                                stdout=subprocess.PIPE)
        if result:
            raise RuntimeError
        result = subprocess.run(
            ['eos', self.eos_url, 'attr', 'set', f'sys.archive.storage_class={storage_class}', path],
            stdout=subprocess.PIPE)
        if result:
            raise RuntimeError

        return self.id_for_file(path=path)
