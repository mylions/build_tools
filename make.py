#!/usr/bin/env python

import os 
import sys
__dir__name__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__name__ + '/scripts')
sys.path.append(__dir__name__ + '/scripts/develop')
sys.path.append(__dir__name__ + '/scripts/develop/vendor')
sys.path.append(__dir__name__ + '/scripts/core_common')
sys.path.append(__dir__name__ + '/scripts/core_common/modules')
sys.path.append(__dir__name__ + '/scripts/core_common/modules/android')
import config
import base
import build_sln
import build_js
import build_server
import deploy
import make_common
import develop
import argparse
import datetime

# custom_current_dir=os.getcwd()
# custom_parent_dir=os.path.dirname(custom_current_dir)

def get_current_time():
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def append_content(content):
  log_file_path='/root/test/build_tools/mylog.txt'
  print("make log_file_path="+log_file_path)
  with open(log_file_path,'a') as f:
    f.write(content)
    f.write('\n')

append_content("in make.py"+get_current_time())

base.check_python()

parser = argparse.ArgumentParser(description="options")
parser.add_argument("--build-only-branding", action="store_true")
args = parser.parse_args()

if (args.build_only_branding):
  base.set_env("OO_BUILD_ONLY_BRANDING", "1")

# parse configuration
config.parse()

base_dir = base.get_script_dir(__file__)

base.set_env("BUILD_PLATFORM", config.option("platform"))
append_content("OO_RUNNING_BRANDING="+base.get_env("OO_RUNNING_BRANDING")+",branding="+config.option("branding"))
# branding
if ("1" != base.get_env("OO_RUNNING_BRANDING")) and ("" != config.option("branding")):
  branding_dir = base_dir + "/../" + config.option("branding")

  if ("1" == config.option("update")):
    is_exist = True
    if not base.is_dir(branding_dir):
      is_exist = False
      base.cmd("git", ["clone", config.option("branding-url"), branding_dir])

    base.cmd_in_dir(branding_dir, "git", ["fetch"], True)

    if not is_exist or ("1" != config.option("update-light")):
      base.cmd_in_dir(branding_dir, "git", ["checkout", "-f", config.option("branch")], True)

    base.cmd_in_dir(branding_dir, "git", ["pull"], True)

  if base.is_file(branding_dir + "/build_tools/make.py"):
    base.check_build_version(branding_dir + "/build_tools")
    base.set_env("OO_RUNNING_BRANDING", "1")
    base.set_env("OO_BRANDING", config.option("branding"))
    base.cmd_in_dir(branding_dir + "/build_tools", "python", ["make.py"])
    exit(0)

# correct defaults (the branding repo is already updated)
config.parse_defaults()

base.check_build_version(base_dir)

append_content("in update"+get_current_time())
# update
if ("1" == config.option("update")):
  repositories = base.get_repositories()
  base.update_repositories(repositories)
append_content("out update"+get_current_time())
base.configure_common_apps()

# developing...
append_content("in develop"+get_current_time())
develop.make()
append_content("out develop"+get_current_time())
append_content("OO_ONLY_BUILD_JS="+base.get_env("OO_ONLY_BUILD_JS"))
# check only js builds
if ("1" == base.get_env("OO_ONLY_BUILD_JS")):
  build_js.make()
  exit(0)

#base.check_tools()
append_content("in make_common make"+get_current_time())
# core 3rdParty
make_common.make()
append_content("out make_common make"+get_current_time())
append_content("module_desktop= "+str(config.check_option("module", "desktop")))
# build updmodule for desktop (only for windows version)
if config.check_option("module", "desktop"):
  config.extend_option("qmake_addon", "URL_WEBAPPS_HELP=https://download.onlyoffice.com/install/desktop/editors/help/v" + base.get_env('PRODUCT_VERSION') + "/apps")

  if "windows" == base.host_platform():
    config.extend_option("config", "updmodule")
    base.set_env("DESKTOP_URL_UPDATES_MAIN_CHANNEL", "https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcast.json")
    base.set_env("DESKTOP_URL_UPDATES_DEV_CHANNEL", "https://download.onlyoffice.com/install/desktop/editors/windows/onlyoffice/appcastdev.json")
append_content("in build_sln make"+get_current_time())
# build
build_sln.make()
append_content("out build_sln make"+get_current_time())
append_content("in build_js make"+get_current_time())
# js
build_js.make()
append_content("out build_js make"+get_current_time())
append_content("in build_server make"+get_current_time())
#server
build_server.make()
append_content("out build_server make"+get_current_time())
append_content("in deploy make"+get_current_time())
# deploy
deploy.make()
append_content("out deploy make"+get_current_time())
append_content("out make.py"+get_current_time())