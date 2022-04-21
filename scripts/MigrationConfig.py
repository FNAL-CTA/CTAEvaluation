class MigrationConfig:
    def __init__(self, file_name):
        self.values = {}
        with open(file_name) as handle:
            for line in handle:
                if not (line.lstrip().startswith('#') or line.isspace()):
                    key, value = line.split()[:2]
                    self.values[key] = value
