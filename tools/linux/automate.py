#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os
import subprocess
import deps
import datetime

# custom_current_dir=os.getcwd()
# custom_parent_dir=os.path.dirname(custom_current_dir)

def get_current_time():
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def append_content(content):
  log_file_path='/root/test/build_tools/mylog.txt'
  print("automate log_file_path="+log_file_path)
  with open(log_file_path,'a',encoding='utf-8') as f:
    f.write(content)
    f.write('\n')

def get_branch_name(directory):
  cur_dir = os.getcwd()
  os.chdir(directory)
  # detect build_tools branch
  #command = "git branch --show-current"
  command = "git symbolic-ref --short -q HEAD"
  current_branch = base.run_command(command)['stdout']
  os.chdir(cur_dir)
  return current_branch

def install_qt():
  # qt
  if not base.is_file("./qt_source_5.9.9.tar.xz"):
    base.download("https://download.qt.io/new_archive/qt/5.9/5.9.9/single/qt-everywhere-opensource-src-5.9.9.tar.xz", "./qt_source_5.9.9.tar.xz")

  if not base.is_dir("./qt-everywhere-opensource-src-5.9.9"):
    base.cmd("tar", ["-xf", "./qt_source_5.9.9.tar.xz"])

  qt_params = ["-opensource",
               "-confirm-license",
               "-release",
               "-shared",
               "-accessibility",
               "-prefix",
               "./../qt_build/Qt-5.9.9/gcc_64",
               "-qt-zlib",
               "-qt-libpng",
               "-qt-libjpeg",
               "-qt-xcb",
               "-qt-pcre",
               "-no-sql-sqlite",
               "-no-qml-debug",
               "-gstreamer", "1.0",
               "-nomake", "examples",
               "-nomake", "tests",
               "-skip", "qtenginio",
               "-skip", "qtlocation",
               "-skip", "qtserialport",
               "-skip", "qtsensors",
               "-skip", "qtxmlpatterns",
               "-skip", "qt3d",
               "-skip", "qtwebview",
               "-skip", "qtwebengine"]

  base.cmd_in_dir("./qt-everywhere-opensource-src-5.9.9", "./configure", qt_params)
  base.cmd_in_dir("./qt-everywhere-opensource-src-5.9.9", "make", ["-j", "4"])
  base.cmd_in_dir("./qt-everywhere-opensource-src-5.9.9", "make", ["install"])
  return

append_content("start automate.py")
append_content("in node_js_setup_14.x "+get_current_time())
if not base.is_file("./node_js_setup_14.x"):
  print("install dependencies...")
  deps.install_deps()
append_content("out node_js_setup_14.x "+get_current_time())
append_content("in qt_build "+get_current_time())
if not base.is_dir("./qt_build"):  
  print("install qt...")
  install_qt()
append_content("out qt_build "+get_current_time())

branch = get_branch_name("../..")

array_args = sys.argv[1:]
array_modules = []
params = []

config = {}
for arg in array_args:
  if (0 == arg.find("--")):
    indexEq = arg.find("=")
    if (-1 != indexEq):
      config[arg[2:indexEq]] = arg[indexEq + 1:]
      params.append(arg[:indexEq])
      params.append(arg[indexEq + 1:])
  else:
    array_modules.append(arg)

if ("branch" in config):
  branch = config["branch"]

print("---------------------------------------------")
print("build branch: " + branch)
print("---------------------------------------------")

modules = " ".join(array_modules)
if "" == modules:
  modules = "desktop builder server"

print("---------------------------------------------")
print("build modules: " + modules)
print("---------------------------------------------")

build_tools_params = ["--branch", branch, 
                      "--module", modules, 
                      "--update", "1",
                      "--qt-dir", os.getcwd() + "/qt_build/Qt-5.9.9"] + params
append_content("build_tools_params="+str(build_tools_params))
base.cmd_in_dir("../..", "./configure.py", build_tools_params)
base.cmd_in_dir("../..", "./make.py")
append_content("end "+get_current_time())


