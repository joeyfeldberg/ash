import configparser
from os import path


class SettingsFile():
    def __init__(self):
        self.config_filename = path.join(path.expanduser("~"), '.ashconfig')
        self.config = configparser.ConfigParser()
        self.ssh_username = "ubuntu"
        self.ssh_identity_file = None
        self.ssh_mux = "cssh"
        self.use_private_ip = True

    def __enter__(self):
        self.config.read(self.config_filename)
        if not self.config.has_section("SSH"):
            self.config.add_section("SSH")

        self.ssh_username = self.config.get(
            section="SSH", option="ssh_username",
            fallback=self.ssh_username)
        self.ssh_identity_file = self.config.get(
            section="SSH", option="ssh_identity_file",
            fallback=self.ssh_identity_file)
        self.ssh_mux = self.config.get(
            section="SSH", option="ssh_mux",
            fallback=self.ssh_mux)
        self.ssh_mux = self.config.get(
            section="SSH", option="use_private_ip",
            fallback=self.use_private_ip)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.config.set(section="SSH", option="ssh_username", value=self.ssh_username)
        if self.ssh_identity_file:
            self.config.set(section="SSH", option="ssh_identity_file", value=self.ssh_identity_file)
        self.config.set(section="SSH", option="ssh_mux", value=self.ssh_mux)
        with open(self.config_filename, 'w') as configfile:
            self.config.write(configfile)
