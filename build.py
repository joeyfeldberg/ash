from pybuilder.core import use_plugin, init
import os

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "sip"
default_task = "install"
version = "0.0.2"

@init
def set_properties(project):
    project.depends_on('python-crontab')
    project.depends_on('boto3')
    project.depends_on(
        'prompt_toolkit',
        '1.0.7',
        'https://github.com/jonathanslenders/python-prompt-toolkit/archive/master.zip'
    )
    project.set_property('coverage_break_build', False)
