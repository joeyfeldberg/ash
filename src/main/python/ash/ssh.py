from subprocess import call


def connect(settings, ips):
    assert len(ips) > 0

    if len(ips) == 1:
        call(["ssh", "{}@{}".format(settings.ssh_username, ips[0])])
    else:
        _connect_mux(settings, ips)


def _connect_mux(settings, ips):
    machines = ["{}@{}".format(settings.ssh_username, ip) for ip in ips]
    ssh_ident = settings.ssh_identity_file

    if settings.ssh_mux == "cssh":
        command = ["cssh"]
        if ssh_ident:
            command.append("-o")
            command.append("'{}'".format(ssh_ident))
    elif settings.ssh_mux == "i2cssh":
        commnad = ["i2cssh", "-F"]
        if ssh_ident:
            command.append("-Xi={}".format(ssh_ident))
    elif settings.ssh_mux == "tmux-cssh":
        command = ["tmux-cssh"]
        if ssh_ident:
            command.append("-i")
            command.append("{}".format(ssh_ident))
        command.append("-sc")
    else:
        raise Exception("No supported ssh_mux type {}".format(settings.ssh_mux))

    call(command + machines)
