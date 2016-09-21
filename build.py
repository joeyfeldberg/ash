from pybuilder.core import use_plugin, init
import os

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "sip"
default_task = "publish"

def zsh_completion_path():
    completion_path = os.path.expanduser('~/.oh-my-zsh/completions')
    if not os.path.exists(completion_path):
        os.makedirs(completion_path)
    return os.path.join(completion_path, "_sip")

@init
def set_properties(project):
    project.depends_on('fuzzywuzzy')
    project.depends_on('python-Levenshtein')
    project.depends_on('python-crontab')
    project.set_property('coverage_break_build', False)

    with open(zsh_completion_path(), "w+") as f:
        with open('src/main/zsh/_sip') as fr:
            f.write(fr.read())
