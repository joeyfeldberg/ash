import shelve
import re
from os import path


class Inventory():
    def __init__(self, providor, sip_cli=None):
        self.status = "ready"
        self.sip_cli = sip_cli
        self.local_inv = []
        self.providor = providor
        self.storage_filename = path.join(path.expanduser("~"), '.sip.data')
        if path.isfile(self.storage_filename):
            self.local_inv = self._read_local_file(self.storage_filename)

    def find_completions(self, name):
        names = self._fuzzyfinder(name, self.local_inv, accessor=lambda x: x.name)
        ips = self._fuzzyfinder(name, self.local_inv, accessor=lambda x: x.private_ip_address)
        types = self._fuzzyfinder(name, self.local_inv, accessor=lambda x: x.instance_type)
        return list(set().union(names, ips, types))

    def refresh(self, on_done=None):
        self.status = "refreshing"
        if on_done:
            def _task():
                self._do_refresh()
                on_done()
            self.sip_cli.eventloop.run_in_executor(_task)
        else:
            self._do_refresh()

    def _do_refresh(self):
        instances = self.providor.get_all()
        with shelve.open(self.storage_filename) as db:
            db['instances'] = instances
            self.local_inv = instances
        self.status = "ready"

    def find_by_name(self, name):
        return next(filter(lambda i: i.name == name, self.local_inv), None)

    def _read_local_file(self, filepath):
        with shelve.open(self.storage_filename) as db:
            return db['instances']

    def _fuzzyfinder(self, text, collection, accessor=lambda x: x):
        suggestions = []
        text = str(text) if not isinstance(text, str) else text
        pat = '.*?'.join(map(re.escape, text))
        regex = re.compile(pat, re.IGNORECASE)
        for item in collection:
            r = regex.search(accessor(item))
            if r:
                suggestions.append((len(r.group()), r.start(), accessor(item), item))
        return [z[-1] for z in suggestions]
