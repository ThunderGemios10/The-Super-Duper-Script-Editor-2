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

from PyQt4 import QtGui
from PyQt4.QtGui import QFileDialog

import os

def get_save_file(parent, default, filter = ""):
  file = QFileDialog.getSaveFileName(parent, directory = default, filter = filter + ";;All files (*.*)")
  if not file == "":
    return os.path.abspath(file)
  else:
    return file

def get_open_file(parent, default, filter = ""):
  file = QFileDialog.getOpenFileName(parent, directory = default, filter = filter + ";;All files (*.*)")
  if not file == "":
    return os.path.abspath(file)
  else:
    return file

def get_existing_dir(parent, default):
  dir = QFileDialog.getExistingDirectory(parent, directory = default)
  if not dir == "":
    return os.path.abspath(dir)
  else:
    return dir

### EOF ###