from subprocess import call


def connect(ip):
    call(["ssh", "ubuntu@{}".format(ip)])
