import os
import shutil
from subprocess import run  # nosec

from setuptools import setup

curr_dir = os.getcwd()
base_dir = os.path.dirname(__file__)
ui_dir = os.path.join(base_dir, 'wahlfang_web')

# we need to build the actual react app into the static folder for us to be able to build a python package from it
os.chdir(ui_dir)
static_dir = os.path.join(ui_dir, 'static')
if os.path.exists(static_dir):
    shutil.rmtree(static_dir)
run(['yarn', 'build'], check=True)  # nosec
os.chdir(curr_dir)

setup()
