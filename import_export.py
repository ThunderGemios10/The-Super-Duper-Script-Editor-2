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
from PyQt4.QtGui import QProgressDialog#, QProgressBar, QTextCursor, QImage, QApplication, QShortcut, QKeySequence
# from PyQt4.QtCore import QString

import glob
import logging
import os
import re
import shutil
import tempfile
import threading
import time

# from bitstring import ConstBitStream

import common

from backup import backup_files
from dupe_db import DupesDB
from list_files import list_all_files
from gim_converter import GimConverter, QuantizeType
from model_pak import ModelPak

_CONV     = GimConverter()
_DUPE_DB  = DupesDB()

SKIP_CONV = ["save_icon0.png", "save_icon0_t.png", "save_new_icon0.png", "save_pic1.png"]

FORCE_QUANTIZE = [
  (re.compile(ur"art_chip_002_\d\d\d.*", re.UNICODE),                         QuantizeType.index8),
  (re.compile(ur"bgd_\d\d\d.*", re.UNICODE),                                  QuantizeType.index8),
  (re.compile(ur"bustup_\d\d_\d\d.*", re.UNICODE),                            QuantizeType.index8),
  (re.compile(ur"(cutin|gallery|kotodama|present)_icn_\d\d\d.*", re.UNICODE), QuantizeType.index8),
]

MIN_INTERVAL = 0.100

# MODEL_PAK = re.compile(ur"bg_\d\d\d")

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

################################################################################
### FUNCTIONS
################################################################################
def import_data01(src, dst, convert_png = True, propogate = True, parent = None):
  pass

def export_data01(src, dst, convert_gim = True, unique = False, parent = None):
  pass

######################################################################
### Importing
######################################################################
def import_umdimage(src, dst, convert_png = True, propogate = True, parent = None):
  src = os.path.abspath(src)
  dst = os.path.abspath(dst)
  if os.path.normcase(src) == os.path.normcase(dst):
    raise ValueError("Cannot import %s. Source and destination directories are the same." % src)
    
  answer = QtGui.QMessageBox.question(
    parent,
    "Import Directory",
    "Importing directory:\n\n" + src + "\n\n" +
    "into directory:\n\n" + dst + "\n\n" +
    "Any affected files will be backed up. Proceed?",
    buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
    defaultButton = QtGui.QMessageBox.No
  )
  
  if answer == QtGui.QMessageBox.No:
    return
  
  progress = QProgressDialog("Finding files...", "Cancel", 0, 1, parent)
  progress.setWindowTitle("Importing...")
  progress.setWindowModality(Qt.Qt.WindowModal)
  progress.setValue(0)
  progress.setAutoClose(False)
  progress.setMinimumDuration(0)
  
  if parent:
    width = parent.width()
    height = parent.height()
    x = parent.x()
    y = parent.y()
  else:
    width   = 1920
    height  = 1080
    x       = 0
    y       = 0
  
  progress.setMaximum(0)
  progress.setValue(0)
  
  # The raw list of files we're importing.
  files = []
  
  # A list of lists, including all dupes of the files being imported, too.
  affected_files = []
  file_count = 0
  
  dupe_base = "umdimage"
  tmp       = tempfile.mkdtemp(prefix = "sdse-")
  
  seen_groups = []
  
  count = 0
  last_update = time.time()
  
  for file in list_all_files(src):
    if progress.wasCanceled():
      break
    
    # Strip our base directory, so we have just a relative file list.
    file = os.path.normpath(os.path.normcase(file[len(src) + 1:]))
    files.append(file)
    
    count += 1
    if time.time() - last_update > MIN_INTERVAL or count % 25 == 0:
      last_update = time.time()
      progress.setLabelText("Finding files...\n" + file)
      # progress.setValue(count)
      progress.setValue(progress.value() ^ 1)
      
      # Re-center the dialog.
      progress_w = progress.geometry().width()
      progress_h = progress.geometry().height()
      
      new_x = x + ((width - progress_w) / 2)
      new_y = y + ((height - progress_h) / 2)
      
      progress.move(new_x, new_y)
    
    affected_files.append([])
    
    if os.path.splitext(file)[1] == ".png" and convert_png and file not in SKIP_CONV:
      file = os.path.splitext(file)[0] + ".gim"
    
    if propogate:
      file_group = _DUPE_DB.group_from_file(os.path.join(dupe_base, file))
    else:
      file_group = None
    
    if file_group in seen_groups:
      continue
    
    # If there are no dupes, just add this file.
    if file_group == None:
      affected_files[-1].append(file)
      file_count += 1
      continue
    
    seen_groups.append(file_group)
    for dupe in _DUPE_DB.files_in_group(file_group):
      # Minus the "umdimage" part
      dupe = dupe[len(dupe_base) + 1:]
      affected_files[-1].append(dupe)
      file_count += 1
  
  progress.setValue(0)
  progress.setMaximum(file_count)
  
  # Make a backup first.
  backup_dir = None
  count = 0
  for file_set in affected_files:
    if progress.wasCanceled():
      break
    for file in file_set:
      if progress.wasCanceled():
        break
      count += 1
      if time.time() - last_update > MIN_INTERVAL or count % 25 == 0:
        last_update = time.time()
        progress.setLabelText("Backing up...\n" + file)
        progress.setValue(count)
        
        # Re-center the dialog.
        progress_w = progress.geometry().width()
        progress_h = progress.geometry().height()
        
        new_x = x + ((width - progress_w) / 2)
        new_y = y + ((height - progress_h) / 2)
        
        progress.move(new_x, new_y)
      
      # It's perfectly possible we want to import some files that
      # don't already exist. Such as when importing a directory
      # with added lines.
      if not os.path.isfile(os.path.join(dst, file)):
        continue
        
      backup_dir = backup_files(dst, [file], suffix = "_IMPORT", backup_dir = backup_dir)
  
  progress.setValue(0)
  
  # And now do our importing.
  import_all_new = False
  skip_all_new = False
  count = 0
  for index, src_file in enumerate(files):
    if progress.wasCanceled():
      break
    
    if os.path.splitext(src_file)[1] == ".png" and convert_png and src_file not in SKIP_CONV:
      tmp_src_file = os.path.join(tmp, os.path.basename(src_file))
      tmp_src_file = os.path.splitext(tmp_src_file)[0] + ".gim"
      quantize = QuantizeType.auto
      for regex, q in FORCE_QUANTIZE:
        if not regex.search(src_file) == None:
          quantize = q
          break
      _CONV.png_to_gim(os.path.join(src, src_file), tmp_src_file, quantize)
      src_file = tmp_src_file
    
    else:
      src_file = os.path.join(src, src_file)
    
    for file in affected_files[index]:
      if progress.wasCanceled():
        break
      
      dst_file = os.path.join(dst, file)
      
      count += 1
      # if count % 25 == 0:
      if time.time() - last_update > MIN_INTERVAL or count % 25 == 0:
        last_update = time.time()
        progress.setLabelText("Importing...\n" + file)
        progress.setValue(count)
        
        # Re-center the dialog.
        progress_w = progress.geometry().width()
        progress_h = progress.geometry().height()
        
        new_x = x + ((width - progress_w) / 2)
        new_y = y + ((height - progress_h) / 2)
        
        progress.move(new_x, new_y)
      
      # We may be allowed to import files that don't exist, but we're
      # going to ask them about it anyway.
      if not os.path.isfile(dst_file):
        if skip_all_new:
          continue
        
        if not import_all_new:
          answer = QtGui.QMessageBox.question(
            parent,
            "File Not Found",
            "File:\n\n" + file + "\n\n" +
            "does not exist in the target directory. Import anyway?",
            buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.YesToAll | QtGui.QMessageBox.No | QtGui.QMessageBox.NoToAll,
            defaultButton = QtGui.QMessageBox.No
          )
          
          if answer == QtGui.QMessageBox.YesToAll:
            import_all_new = True
            skip_all_new = False
          elif answer == QtGui.QMessageBox.NoToAll:
            skip_all_new = True
            import_all_new = False
            continue
          elif answer == QtGui.QMessageBox.No:
            continue
      
      basedir = os.path.dirname(dst_file)
      if not os.path.isdir(basedir):
        os.makedirs(basedir)
      
      shutil.copy2(src_file, dst_file)
  
  shutil.rmtree(tmp)
  progress.close()

def import_umdimage2(src, dst, convert_png = True, propogate = True, parent = None):
  src = os.path.abspath(src)
  dst = os.path.abspath(dst)
  if os.path.normcase(src) == os.path.normcase(dst):
    raise ValueError("Cannot import %s. Source and destination directories are the same." % src)
    
  answer = QtGui.QMessageBox.question(
    parent,
    "Import Directory",
    "Importing directory:\n\n" + src + "\n\n" +
    "into directory:\n\n" + dst + "\n\n" +
    "Any affected files will be backed up. Proceed?",
    buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
    defaultButton = QtGui.QMessageBox.No
  )
  
  if answer == QtGui.QMessageBox.No:
    return
  
  progress = QProgressDialog("Importing...", "Cancel", 0, 0, parent)
  progress.setWindowTitle("Importing...")
  progress.setWindowModality(Qt.Qt.WindowModal)
  progress.setValue(0)
  progress.setAutoClose(False)
  progress.setMinimumDuration(0)
  
  tmp_dst     = tempfile.mkdtemp(prefix = "sdse-")
  backup_dir  = None
  
  for pak in glob.iglob(os.path.join(src, "bg_*.pak")):
    if progress.wasCanceled():
      break
    
    pak_name    = os.path.basename(pak)
    backup_dir  = backup_files(dst, [pak_name], suffix = "_IMPORT", backup_dir = backup_dir)
    
    # If we have a regular file with the bg_*.pak name, then just drop it in.
    if os.path.isfile(pak):
      progress.setLabelText("Importing:\n" + pak_name)
      progress.setValue(progress.value() ^ 1)
      shutil.copy2(pak, os.path.join(dst, pak_name))
    
    # Otherwise, if it's a directory, insert all the textures we find
    # into the target bg_*.pak file.
    elif os.path.isdir(pak):
      for image in list_all_files(pak):
        if progress.wasCanceled():
          break
        
        ext = os.path.splitext(image)[1].lower()
        if ext == ".png" and not convert_png:
          continue
        
        base_name = image[len(src) + 1:]
        dst_files = []
        
        if propogate:
          dupe_name = os.path.splitext(base_name)[0] + ".gim"
          dupe_name = os.path.join("umdimage2", dupe_name)
          dupe_name = os.path.normpath(os.path.normcase(dupe_name))
        
          dupes = _DUPE_DB.files_in_same_group(dupe_name)
          
          if dupes == None:
            dupes = [dupe_name]
          
          for dupe in dupes:
            dst_file = dupe[10:] # chop off the "umdimage2/"
            dst_file = os.path.splitext(dst_file)[0] + ext # original extension
            dst_file = os.path.join(tmp_dst, dst_file)
            dst_files.append(dst_file)
        
        else:
          dst_files = [os.path.join(tmp_dst, base_name)]
        
        for dst_file in dst_files:
          try:
            os.makedirs(os.path.dirname(dst_file))
          except:
            pass
          shutil.copy(image, dst_file)
      
      if progress.wasCanceled():
        break
    
      progress.setLabelText("Inserting textures into:\n" + pak_name)
      progress.setValue(progress.value() ^ 1)
      
      pak_dir   = os.path.join(tmp_dst, pak_name)
      pak_file  = os.path.join(dst, pak_name)
      
      # If we didn't copy anything over, just move on.
      if not os.path.isdir(pak_dir):
        continue
      
      thread = threading.Thread(target = insert_textures, args = (pak_dir, pak_file))
      thread.start()
      
      while thread.isAlive():
        thread.join(MIN_INTERVAL)
        progress.setValue(progress.value() ^ 1)
        
        if progress.wasCanceled():
          progress.setLabelText("Canceling...")
  
  shutil.rmtree(tmp_dst)
  progress.close()

######################################################################
### Exporting
######################################################################
def export_umdimage(src, dst, convert_gim = True, unique = False, parent = None):
  src = os.path.abspath(src)
  dst = os.path.abspath(dst)
  if os.path.normcase(src) == os.path.normcase(dst):
    raise ValueError("Cannot export %s. Source and destination directories are the same." % src)
    
  answer = QtGui.QMessageBox.question(
    parent,
    "Export Directory",
    "Exporting directory:\n\n" + src + "\n\n" +
    "into directory:\n\n" + dst + "\n\n" +
    "Proceed?",
    buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
    defaultButton = QtGui.QMessageBox.No
  )
  
  if answer == QtGui.QMessageBox.No:
    return
  
  progress = QProgressDialog("Exporting...", "Cancel", 0, 0, parent)
  progress.setWindowTitle("Exporting...")
  progress.setWindowModality(Qt.Qt.WindowModal)
  progress.setValue(0)
  progress.setAutoClose(False)
  progress.setMinimumDuration(0)
  
  if parent:
    width = parent.width()
    height = parent.height()
    x = parent.x()
    y = parent.y()
  else:
    width   = 1920
    height  = 1080
    x       = 0
    y       = 0
  
  seen_groups = []
  
  count = 0
  last_update = time.time()
  progress.setMaximum(60000)
  
  for filename in list_all_files(src):
    if progress.wasCanceled():
      break
    
    count += 1
    if time.time() - last_update > MIN_INTERVAL or count % 25 == 0:
      last_update = time.time()
      progress.setLabelText("Exporting...\n" + filename)
      progress.setValue(count)
      
      # Re-center the dialog.
      progress_w = progress.geometry().width()
      progress_h = progress.geometry().height()
      
      new_x = x + ((width - progress_w) / 2)
      new_y = y + ((height - progress_h) / 2)
      
      progress.move(new_x, new_y)
    
    base_name = filename[len(src) + 1:]
    if unique:
      dupe_name = os.path.join("umdimage", base_name)
      dupe_name = os.path.normpath(os.path.normcase(dupe_name))
      
      group = _DUPE_DB.group_from_file(dupe_name)
      
      if group in seen_groups:
        continue
      
      if not group == None:
        seen_groups.append(group)
    
    dst_file = os.path.join(dst, base_name)
    dst_dir  = os.path.dirname(dst_file)
    ext      = os.path.splitext(dst_file)[1].lower()
    
    try:
      os.makedirs(dst_dir)
    except:
      pass
    
    if ext == ".gim" and convert_gim:
      dst_file = os.path.splitext(dst_file)[0] + ".png"
      _CONV.gim_to_png(filename, dst_file)
    else:
      shutil.copy2(filename, dst_file)
  
  progress.close()

def export_umdimage2(src, dst, convert_gim = True, unique = False, parent = None):
  src = os.path.abspath(src)
  dst = os.path.abspath(dst)
  if os.path.normcase(src) == os.path.normcase(dst):
    raise ValueError("Cannot export %s. Source and destination directories are the same." % src)
    
  answer = QtGui.QMessageBox.question(
    parent,
    "Export Directory",
    "Exporting directory:\n\n" + src + "\n\n" +
    "into directory:\n\n" + dst + "\n\n" +
    "Proceed?",
    buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
    defaultButton = QtGui.QMessageBox.No
  )
  
  if answer == QtGui.QMessageBox.No:
    return
  
  progress = QProgressDialog("Exporting...", "Cancel", 0, 0, parent)
  progress.setWindowTitle("Exporting...")
  progress.setWindowModality(Qt.Qt.WindowModal)
  progress.setValue(0)
  progress.setAutoClose(False)
  progress.setMinimumDuration(0)
  
  if unique:
    tmp_dst = tempfile.mkdtemp(prefix = "sdse-")
  else:
    tmp_dst = dst
  
  seen_groups = []
  
  for pak in glob.iglob(os.path.join(src, "bg_*.pak")):
    if progress.wasCanceled():
      break
    
    pak_name = os.path.basename(pak)
    out_dir  = os.path.join(tmp_dst, pak_name)
  
    progress.setLabelText("Extracting:\n" + pak)
    
    thread = threading.Thread(target = extract_model_pak, args = (pak, out_dir, convert_gim))
    thread.start()
    
    while thread.isAlive():
      thread.join(MIN_INTERVAL)
      progress.setValue(progress.value() ^ 1)
      
      if progress.wasCanceled():
        progress.setLabelText("Canceling...")
    
    if progress.wasCanceled():
      break
  
    if unique:
      for img in list_all_files(out_dir):
        img_base  = img[len(tmp_dst) + 1:]
        dupe_name = os.path.splitext(img_base)[0] + ".gim"
        dupe_name = os.path.join("umdimage2", dupe_name)
        dupe_name = os.path.normpath(os.path.normcase(dupe_name))
        
        group = _DUPE_DB.group_from_file(dupe_name)
        
        if group in seen_groups:
          continue
        
        if not group == None:
          seen_groups.append(group)
        
        dst_file = os.path.join(dst, img_base)
        dst_dir  = os.path.dirname(dst_file)
        
        try:
          os.makedirs(dst_dir)
        except:
          pass
        
        shutil.copy2(img, dst_file)
      
      shutil.rmtree(out_dir)
  
  if unique:
    shutil.rmtree(tmp_dst)
  
  progress.close()

######################################################################
### Models/textures
######################################################################
def extract_model_pak(filename, out_dir, to_png):
  pak = ModelPak(filename = filename)
  pak.extract(out_dir, to_png)

def insert_textures(pak_dir, filename):
  
  pak = ModelPak(filename = filename)
  
  for gmo_name in os.listdir(pak_dir):
    full_path = os.path.join(pak_dir, gmo_name)
    if not os.path.isdir(full_path):
      _LOGGER.warning("Not a directory of textures. Skipped importing %s to %s" % (full_path, filename))
      continue
  
    gmo_id = pak.id_from_name(gmo_name)
    if gmo_id == None:
      _LOGGER.warning("GMO %s does not exist in %s" % (gmo_name, filename))
      continue
    
    gmo = pak.get_gmo(gmo_id)
    if gmo == None:
      _LOGGER.warning("Failed to retrieve GMO %s from %s" % (gmo_name, filename))
      continue
    
    for img in os.listdir(os.path.join(pak_dir, gmo_name)):
      name, ext = os.path.splitext(img)
      
      if ext.lower() == ".gim":
        is_png = False
      elif ext.lower() == ".png":
        is_png = True
      else:
        _LOGGER.warning("Did not insert %s into %s" % (img, gmo_name))
        continue
      
      gim_id = int(name)
      if is_png:
        gmo.replace_png_file(gim_id, os.path.join(pak_dir, gmo_name, img))
      else:
        gmo.replace_gim_file(gim_id, os.path.join(pak_dir, gmo_name, img))
    
    pak.replace_gmo(gmo_id, gmo)
  
  pak.save(filename)

if __name__ == "__main__":
  import sys
  app = QtGui.QApplication(sys.argv)
  
  handler = logging.StreamHandler(sys.stdout)
  # logging.getLogger(common.LOGGER_NAME).addHandler(handler)
  
  # export_umdimage2("Y:/Danganronpa/Danganronpa_BEST/umdimage2", "wip/umdimage3", convert_gim = True, unique = True)
  # export_umdimage("Y:/Danganronpa/Danganronpa_BEST/umdimage", "wip/umdimage-out", convert_gim = True, unique = True)
  # import_umdimage2("Y:/Danganronpa/Danganronpa_BEST/image-editing/umdimage2-edited-png", "wip/umdimage2-orig")
  # import_umdimage2("wip/umdimage2-edited-png", "wip/umdimage2-orig", convert_png = False)
  # export_umdimage2("wip/umdimage2-orig", "wip/umdimage2-xxx", convert_gim = True, unique = True)
  # import_umdimage("wip/umdimage-import", "wip/umdimage-test")
  import_umdimage("wip/umdimage-import", "wip/umdimage-test2", propogate = True, convert_png = True)
  # import_umdimage("wip/umdimage-import", "wip/umdimage-test3", propogate = False)
  
  # extract_model_pak("wip/test/bg_042.pak", "wip/test")
  # import_model_pak("wip/test/bg_042-eng", "wip/test/bg_042.pak")
  # extract_model_pak("wip/test/bg_042.pak", "wip/test")

### EOF ###