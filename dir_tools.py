################################################################################
### Copyright © 2012-2013 BlackDragonHunt
### 
### This file is part of the Super Duper Script Editor.
### 
### The Super Duper Script Editor is free software: you can redistribute it
### and/or modify it under the terms of the GNU General Public License as
### published by the Free Software Foundation, either version 3 of the License,
### or (at your option) any later version.
### 
### The Super Duper Script Editor is distributed in the hope that it will be
### useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
### 
### You should have received a copy of the GNU General Public License
### along with the Super Duper Script Editor.
### If not, see <http://www.gnu.org/licenses/>.
################################################################################

import os
import re
import subprocess

SCRIPT_DIR          = os.path.join("jp", "script")
SCRIPT_BIN_DIR      = os.path.join("jp", "bin")
# RE_SCRIPT_PAK_SKIP  = re.compile(ur"^(script_pak_.*?)\.pak", re.UNICODE | re.IGNORECASE)
RE_SCRIPT_PAK       = re.compile(ur"^(script_pak_(e\d\d|novel))_\d\d\d\.lin", re.UNICODE | re.IGNORECASE)
RE_CONSOLIDATE      = re.compile(ur"(data01[\\\/])?jp[\\\/](script|bin)[\\\/]", re.UNICODE | re.S)

def normalize(path):
  return os.path.normpath(os.path.normcase(path))

def show_in_explorer(directory):
  subprocess.Popen(["explorer", "/select,", directory])

def expand_script_pak(directory):
  
  directory = normalize(directory)
  match = RE_SCRIPT_PAK.match(directory)
  if match:# and not RE_SCRIPT_PAK_SKIP.match(directory):
    directory = os.path.join(match.group(1) + ".pak", directory)
  
  return directory

def expand_dir(directory):

  directory = expand_script_pak(directory)
  if not directory[:len(SCRIPT_DIR)] == SCRIPT_DIR and not directory[:len(SCRIPT_BIN_DIR)] == SCRIPT_BIN_DIR:
    if directory[:4] == "bin_" or directory[:12] == "twilight_all":
      directory = os.path.join(SCRIPT_BIN_DIR, directory)
    else:
      directory = os.path.join(SCRIPT_DIR, directory)
  
  return directory

def consolidate_dir(directory):
  return RE_CONSOLIDATE.sub(ur"", directory)

### EOF ###