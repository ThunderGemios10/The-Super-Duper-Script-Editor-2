# -*- coding: utf-8 -*-
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

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtGui import QProgressDialog
from PyQt4.QtCore import QProcess, QString

import bitstring
from bitstring import BitStream, ConstBitStream
from tempfile import TemporaryFile

import csv
import logging
import os
import re
import shutil
import tempfile

import common
import eboot_patch

from .pak import pack_dir
from list_files import list_all_files

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

OUTPUT_RE = re.compile(ur"([\d\.]+)%")

class CpkPacker():
  def __init__(self, parent = None):
    self.parent   = parent
    self.process  = None
  
  def __pack_cpk(self, csv, cpk):
    
    self.progress.setValue(0)
    self.progress.setMaximum(100000)
    self.progress.setLabelText("Building %s" % cpk)
    
    process = QProcess()
    process.start("tools/cpkmakec", [csv, cpk, "-align=2048", "-mode=FILENAME"])
    
    percent = 0
    
    while not process.waitForFinished(100):
    
      output = QString(process.readAll())
      output = output.split("\n", QString.SkipEmptyParts)
      
      for line in output:
        line = common.qt_to_unicode(line)
        match = OUTPUT_RE.search(line)
        
        if match == None:
          continue
        
        percent = float(match.group(1)) * 1000
      
      self.progress.setValue(percent)
      percent += 1
  
  def __cache_outdated(self, src_dir, cache_file):
    if not os.path.isfile(cache_file):
      return True
    
    cache_updated = os.path.getmtime(cache_file)
    
    for src_file in list_all_files(src_dir):
      if os.path.getmtime(src_file) > cache_updated:
        return True
    
    return False

  def create_archives(self):
    
    try:
      self.width = self.parent.width()
      self.height = self.parent.height()
      self.x = self.parent.x()
      self.y = self.parent.y()
    except:
      self.width = 1920
      self.height = 1080
      self.x = 0
      self.y = 0
    
    self.progress = QProgressDialog("Reading...", QtCore.QString(), 0, 7600, self.parent)
    self.progress.setWindowModality(Qt.Qt.WindowModal)
    self.progress.setValue(0)
    self.progress.setAutoClose(False)
    self.progress.setMinimumDuration(0)
    
    USRDIR     = os.path.join(common.editor_config.iso_dir, "PSP_GAME", "USRDIR")
    eboot_path = os.path.join(common.editor_config.iso_dir, "PSP_GAME", "SYSDIR", "EBOOT.BIN")
    
    eboot = BitStream(filename = eboot_path)
    eboot = eboot_patch.apply_eboot_patches(eboot)
    
    # So we can loop. :)
    ARCHIVE_INFO = [
      {
        "dir":  common.editor_config.data00_dir,
        "cpk":  os.path.join(USRDIR, "data00.cpk"),
        "csv":  os.path.join("data", "data00.csv" if not common.editor_config.quick_build else "data00-quick.csv"),
        "name": "data00.cpk",
        "pack": common.editor_config.pack_data00,
      },
      {
        "dir":  common.editor_config.data01_dir,
        "cpk":  os.path.join(USRDIR, "data01.cpk"),
        "csv":  os.path.join("data", "data01.csv" if not common.editor_config.quick_build else "data01-quick.csv"),
        "name": "data01.cpk",
        "pack": common.editor_config.pack_data01,
      },
    ]
    
    # temp_dir = tempfile.mkdtemp(prefix = "sdse-")
    temp_dir = common.editor_config.build_cache
    
    for archive in ARCHIVE_INFO:
      
      if not archive["pack"]:
        continue
      
      self.progress.setWindowTitle("Building " + archive["name"])
      
      csv_template_f  = open(archive["csv"], "rb")
      csv_template    = csv.reader(csv_template_f)
      
      csv_out_path    = os.path.join(temp_dir, "cpk.csv")
      csv_out_f       = open(csv_out_path, "wb")
      csv_out         = csv.writer(csv_out_f)
      
      for row in csv_template:
        if len(row) < 4:
          continue
        
        base_path = row[0]
        
        real_path = os.path.join(archive["dir"], base_path)
        out_path  = os.path.join(temp_dir, archive["name"], base_path)
        
        self.progress.setValue(self.progress.value() + 1)
        self.progress.setLabelText("Reading...\n%s" % real_path)
        
        # All items in the CPK list should be files.
        # Therefore, if we have a directory, then it needs to be packed.
        if os.path.isdir(real_path):
          if self.__cache_outdated(real_path, out_path):
            out_dir = os.path.dirname(out_path)
            try:
              os.makedirs(out_dir)
            except:
              pass
            
            data = pack_dir(real_path)
            with open(out_path, "wb") as out_file:
              data.tofile(out_file)
            del data
            
        elif os.path.isfile(real_path):
          # If it's a file, though, we can just use it directly.
          out_path = real_path
          
        row[0] = out_path
        csv_out.writerow(row)
      
      csv_template_f.close()
      csv_out_f.close()
      
      self.__pack_cpk(csv_out_path, archive["cpk"])
    
    self.progress.setWindowTitle("Building...")
    self.progress.setLabelText("Saving EBOOT.BIN...")
    self.progress.setValue(self.progress.maximum())
    
    with open(eboot_path, "wb") as f:
      eboot.tofile(f)
    
    # self.progress.setLabelText("Deleting temporary files...")
    # shutil.rmtree(temp_dir)
    self.progress.close()

if __name__ == "__main__":
  pass
  # import sys
  # app = QtGui.QApplication(sys.argv)
  
  # packer = DatPacker()
  
  #start = time.time()
  # packer.create_archives()
  #print "Took %s seconds to create the archives." % (time.time() - start)

### EOF ###
