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

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtGui import QProgressDialog, QProgressBar
from PyQt4.QtCore import QProcess, QString

import os
import re

import common

OUTPUT_RE = re.compile(ur".*?([0-9\.]+)\%\sdone")

class IsoBuilder():
  def __init__(self, parent = None):
    self.parent = parent
    self.process = None
  
  def __parse_output(self):
    if not self.process:
      return
    
    output = QString(self.process.readAll())
    output = output.split("\n", QString.SkipEmptyParts)
    
    for line in output:
      line = common.qt_to_unicode(line)
      
      match = OUTPUT_RE.match(line)
      
      if match == None:
        continue
      
      percent = float(match.group(1))
      self.progress.setValue(percent)
  
  def build_iso(self, directory, iso_file):
    
    if self.process:
      return
    
    directory = os.path.abspath(directory)
    iso_file  = os.path.abspath(iso_file)
    
    self.progress = QProgressDialog("Building ISO...", QtCore.QString(), 0, 0, self.parent)
    self.progress.setWindowTitle("Building ISO")
    self.progress.setWindowModality(Qt.Qt.WindowModal)
    self.progress.setAutoClose(False)
    self.progress.setMinimumDuration(1000)
    
    self.progress.show()
    self.progress.setValue(0)
    self.progress.setMaximum(100)
    
    self.process = QProcess()
    self.process.finished.connect(self.__build_finished)
    self.process.setReadChannel(QProcess.StandardError)
    self.process.readyRead.connect(self.__parse_output)
    self.process.start("tools/mkisofs", ["-sort", "data/file_order.txt", "-iso-level", "4", "-xa", "-A", "PSP GAME", "-V", "DANGANRONPA", "-sysid", "PSP GAME", "-volset", "DANGANRONPA", "-p", "SPIKE", "-publisher", "SPIKE", "-o", iso_file, directory])
    
  def __build_finished(self, code, status):
    self.progress.close()
    self.process = None

if __name__ == "__main__":
  import sys
  app = QtGui.QApplication(sys.argv)
  
  builder = IsoBuilder()
  builder.build_iso("X:\\Danganronpa\\Danganronpa_BEST\\!ISO_EDITED", "X:\\Danganronpa\\Danganronpa_BEST\\test2.iso")
  builder.process.waitForFinished(-1)

### EOF ###