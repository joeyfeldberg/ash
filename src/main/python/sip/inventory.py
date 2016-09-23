from os import path
from fuzzywuzzy import process


def create(providor):
    return Inventory(providor)


class Inventory():
    def __init__(self, providor):
        self.local_inv = []
        self.providor = providor
        self.storage_filename = path.join(path.expanduser("~"), '.sip_data')
        if path.isfile(self.storage_filename):
            self.local_inv = self.read_local_file(self.storage_filename)

    def find_completions(self, name):
        res = process.extractBests(name, self.local_inv,
                                   score_cutoff=30, limit=20)
        return [i[0] for i in res]

    def refresh(self):
        instances = self.providor.get_all()
        with open(self.storage_filename, "w+") as f:
            f.write('\n'.join("{},{}".format(x[0], x[1]) for x in instances))

    def read_local_file(self, filepath):
        with open(self.storage_filename) as f:
            return [tuple(i.split(',')) for i in f.read().splitlines()]
