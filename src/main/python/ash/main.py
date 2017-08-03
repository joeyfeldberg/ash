import argparse
import re


from prompt_toolkit.shortcuts import create_eventloop

from ash.cron import install_cron
from ash.cli import ashCLI
from ash.ssh import connect
from ash.settings import SettingsFile

ipv4_address = re.compile('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')


def toolkit_main(settings):
    try:
        eventloop = create_eventloop()
        ret = ashCLI(settings, eventloop).create_application().run()
        if ret:
            if ret.document.selection is None:
                rows = ret.document.current_line
            else:
                rows = ret.copy_selection().text

            ips = ipv4_address.findall(rows)
            connect(settings, ips)

    finally:
        eventloop.close()


def parse_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh_inventory', action='store_true')
    parser.add_argument('--install_cron', metavar="minutes")
    parser.add_argument('--username', default="ubuntu")
    parser.add_argument('--indentity_file', default=None)
    return parser.parse_args()


def run():
    opts = parse_opts()

    if opts.install_cron:
        install_cron(int(opts.install_cron))
    elif opts.refresh_inventory:
        from ash.inventory import Inventory
        from ash.ec2_providor import EC2Providor
        inv = Inventory(EC2Providor())
        inv.refresh()
    else:
        with SettingsFile() as settings:
            return toolkit_main(settings)


if __name__ == '__main__':
    run()
