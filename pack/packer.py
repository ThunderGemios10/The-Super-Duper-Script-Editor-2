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
from PyQt4.QtGui import QApplication

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
    self.progress.setMaximum(1000)
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
      
      toc_info = {}
      file_list = None
      
      if archive["toc"]:
        file_list = []
        
        toc = get_toc(eboot, archive["toc"])
        
        for entry in toc:
          filename  = entry["filename"]
          pos_pos   = entry["file_pos_pos"]
          len_pos   = entry["file_len_pos"]
          
          toc_info[filename] = [pos_pos, len_pos]
          file_list.append(filename)
      
      # Causes memory issues if I use the original order, for whatever reason.
      file_list = None
      
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
        
      self.file_count += 1
      if self.file_count % 25 == 0:
        self.progress.setLabelText("Reading...\n" + full_path)
        self.progress.setValue(self.file_count)
        
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
      
      # We're playing fast and loose with the file count anyway, so why not?
      self.file_count += 1
      self.progress.setValue(self.file_count)
      self.progress.setLabelText("Saving " + archive["name"] + "...")
      
      if archive["toc"]:
        for entry in table_of_contents:
          if not entry in toc_info:
            _LOGGER.warning("%s missing from %s table of contents." % (entry, archive["name"]))
            continue
          
          file_pos  = table_of_contents[entry]["pos"]
          file_size = table_of_contents[entry]["size"]
          
          eboot.overwrite(BitStream(uintle = file_pos, length = 32),  toc_info[entry][0] * 8)
          eboot.overwrite(BitStream(uintle = file_size, length = 32), toc_info[entry][1] * 8)
      
      del table_of_contents

  def pack_dir(self, dir, handler, file_list = None, align_toc = 16, align_files = 16, eof = False):
    
    table_of_contents = {}
    
    if file_list == None:
      file_list = sorted(os.listdir(dir))
      
    num_files    = len(file_list)
    
    toc_length = (num_files + 1) * 4
    
    if eof:
      toc_length += 1
    
    if toc_length % align_toc > 0:
      toc_length += align_toc - (toc_length % align_toc)
    
    handler.seek(0)
    handler.write(struct.pack("<I", num_files))
    handler.write(bytearray(toc_length - 4))
    
    for file_num, item in enumerate(file_list):
      full_path = os.path.join(dir, item)
    
      if os.path.isfile(full_path):
        
        basename = os.path.basename(item)
        basename, ext = os.path.splitext(basename)
        
        # Special handling for certain data types.
        if ext == ".txt":
          data = self.pack_txt(full_path)
        
        # anagram_81.dat is not a valid anagram file. <_>
        elif basename[:8] == "anagram_" and ext == ".dat" and not basename == "anagram_81":
          anagram = AnagramFile(full_path)
          data    = anagram.pack(for_game = True).bytes
        
        else:
          with open(full_path, "rb") as f:
            data = f.read()
      
      else:
      
        temp_align_toc = 16
        temp_align_files = 4
        
        if item in SPECIAL_ALIGN:
          temp_align_toc = SPECIAL_ALIGN[item][0]
          temp_align_files = SPECIAL_ALIGN[item][1]
        elif os.path.basename(dir) in SPECIAL_ALIGN and len(SPECIAL_ALIGN[os.path.basename(dir)]) == 4:
          temp_align_toc = SPECIAL_ALIGN[os.path.basename(dir)][2]
          temp_align_files = SPECIAL_ALIGN[os.path.basename(dir)][3]
        
        if os.path.splitext(full_path)[1].lower() == ".lin":
          data = self.pack_lin(full_path)
        
        else:
          data = io.BytesIO()
          with io.BufferedWriter(data) as fh:
            self.pack_dir(full_path, fh, align_toc = temp_align_toc, align_files = temp_align_files, eof = eof)
            fh.flush()
            data = data.getvalue()
      
      data = bytearray(data)
      file_size = len(data)
      padding = 0
      
      if file_size % align_files > 0:
        padding = align_files - (file_size % align_files)
        data.extend(bytearray(padding))
      
      handler.seek(0, io.SEEK_END)
      file_pos = handler.tell()
      handler.write(data)
      handler.seek((file_num + 1) * 4)
      handler.write(struct.pack("<I", file_pos))
      
      del data
      
    self.progress.setWindowTitle("Building...")
    self.progress.setLabelText("Saving EBOOT.BIN...")
    self.progress.setValue(self.progress.maximum())

      
    # Text replacement
    to_replace = eboot_text.get_eboot_text()
    for replacement in to_replace:
    
      orig = bytearray(replacement.orig, encoding = replacement.enc)
      
      # If they left something blank, write the original text back.
      if len(replacement.text) == 0:
        data = orig
      else:
        data = bytearray(replacement.text, encoding = replacement.enc)
      
      pos  = replacement.pos.int + eboot_offset
      
      padding = len(orig) - len(data)
      if padding > 0:
        # Null bytes to fill the rest of the space the original took.
        data.extend(bytearray(padding))
      
      data = ConstBitStream(bytes = data)
      eboot.overwrite(data, pos * 8)
    
    eboot_out = os.path.join(common.editor_config.iso_dir, "PSP_GAME", "SYSDIR", "EBOOT.BIN")
    
    with open(eboot_out, "wb") as f:
      eboot.tofile(f)
    
    self.progress.close()
    
    # self.progress.setLabelText("Deleting temporary files...")
    # shutil.rmtree(temp_dir)
    
        # Re-center the dialog.
        progress_w = self.progress.geometry().width()
        progress_h = self.progress.geometry().height()
        
        new_x = self.x + ((self.width - progress_w) / 2)
        new_y = self.y + ((self.height - progress_h) / 2)
        
        self.progress.move(new_x, new_y)
      
      table_of_contents[item] = {}
      table_of_contents[item]["size"] = file_size
      table_of_contents[item]["pos"]  = file_pos
    
    if eof:
      handler.seek(0, io.SEEK_END)
      archive_len = handler.tell()
      handler.seek((num_files + 1) * 4)
      handler.write(struct.pack("<I", archive_len))
    
    return table_of_contents
  
  def pack_txt(self, filename):
    
    if os.path.basename(os.path.dirname(filename)) in SCRIPT_NONSTOP:
      is_nonstop = True
    else:
      is_nonstop = False
  
    text = text_files.load_text(filename)
    text = RE_SCRIPT.sub(u"\g<1>", text)
    
    # Nonstop Debate lines need an extra newline at the end
    # so they show up in the backlog properly.
    if is_nonstop and not text[-1] == "\n":
      text += "\n"
    
    return SCRIPT_BOM.bytes + bytearray(text, encoding = "UTF-16LE") + SCRIPT_NULL.bytes
    
  def pack_lin(self, dir):
    
    # Collect our files.
    file_list = sorted(list_all_files(dir))
    
    txt = [filename for filename in file_list if os.path.splitext(filename)[1].lower() == ".txt"]
    wrd = [filename for filename in file_list if os.path.splitext(filename)[1].lower() == ".wrd"]
    py  = [filename for filename in file_list if os.path.splitext(filename)[1].lower() == ".py"]
    
    # If there are more than one for whatever reason, just take the first.
    # We only have use for a single wrd or python file.
    wrd = wrd[0] if wrd else None
    py  = py[0]  if py  else None
    
    # Prepare our temporary output directory.
    temp_dir = tempfile.mkdtemp(prefix = "sdse-")
    
    # Where we're outputting our wrd file, regardless of whether it's a python
    # file or a raw binary data file.
    wrd_dst = os.path.join(temp_dir, "0.scp.wrd")
    
    if py:
      # _LOGGER.info("Compiling %s to binary." % py)
      try:
        wrd_file = WrdFile(py)
      except:
        _LOGGER.warning("%s failed to compile. Parsing wrd file instead. Exception info:\n%s" % (py, traceback.format_exc()))
        shutil.copy(wrd, wrd_dst)
      else:
        # If we succeeded in loading the python file, compile it to binary.
        # wrd_file.save_bin(wrd)
        wrd_file.save_bin(wrd_dst)
    
    else:
      shutil.copy(wrd, wrd_dst)
    
    # Pack the text files in-place to save us a bunch of copying
    # and then move it to the tmp directory with the wrd file.
    if txt:
      with io.FileIO(os.path.join(temp_dir, "1.dat"), "w") as h:
        self.pack_dir(dir, h, file_list = txt)
    
    # Then pack it like normal.
    data = io.BytesIO()
    with io.BufferedWriter(data) as h:
      self.pack_dir(temp_dir, h)
      h.flush()
      data = data.getvalue()
    
    shutil.rmtree(temp_dir)
    
    return data

if __name__ == "__main__":
  pass
  # import sys
  # app = QtGui.QApplication(sys.argv)
  
  packer = CpkPacker()
  
  #start = time.time()
  packer.create_archives()
  #print "Took %s seconds to create the archives." % (time.time() - start)

### EOF ###
