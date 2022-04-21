import json
import subprocess


class EosInfo:
    def __init__(self, server: str):
        self.eos_ids = {}
        self.server = server

    def id_for_file(self, path: str) -> int:
        """
        Cache and retrieve the IDs of a path

        :param path: The full path of the file or directory to get the ID for
        :return: the ID number of the path
        """
        if path in self.eos_ids:
            return self.eos_ids[path]
        eos_url = f"root://{self.server}"
        result = subprocess.run(['eos', '--json', eos_url, 'info', path], stdout=subprocess.PIPE)
        eos_info = json.loads(result.stdout.decode('utf-8'))
        try:
            self.eos_ids[path] = int(eos_info['id'])
        except KeyError:
            return None
        except ValueError:
            raise RuntimeError('Could not determine EOS file ID')
        return self.eos_ids[path]
