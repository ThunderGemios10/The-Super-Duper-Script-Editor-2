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

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtGui import QFileDialog, QProgressDialog
from ui.wizard import Ui_SetupWizard

import base64
import cStringIO
import glob
import os
import shutil
import sys
import threading
import zipfile
from bitstring import ConstBitStream, BitStream

import common
from dialog_fns import get_save_file, get_open_file, get_existing_dir
from eboot_patch import apply_eboot_patches
# from extract import extract_umdimage, extract_pak
# from extract.eboot import UMDIMAGES
from extract.cpk import extract_cpk
# from extract.pak import extract_pak
from font_parser import font_bmp_to_alpha
from gim_converter import GimConverter
from gmo_file import GmoFile

DATA00_CPK      = os.path.join("PSP_GAME", "USRDIR", "data00.cpk")
DATA01_CPK      = os.path.join("PSP_GAME", "USRDIR", "data01.cpk")
VOICE_AWB       = os.path.join("data00", "jp", "voice", "voice.awb")

DATA00_DIR      = "data00"
DATA01_DIR      = "data01"
VOICE_DIR       = "voice"
CHANGES_DIR     = "!changes"
BACKUP_DIR      = "!backup"
EDITED_ISO_DIR  = "!ISO_EDITED"
EDITED_ISO_FILE = "[PSP] SDR2 [Edited].iso"

EDITOR_DATA_DIR = "!editor"
DUPES_CSV       = "dupes.csv"
SIMILARITY_DB   = "similarity-db.sql"

THREAD_TIMEOUT = 0.1

class SetupWizard(QtGui.QDialog):
  def __init__(self, parent=None):
    super(SetupWizard, self).__init__(parent)
    
    self.ui = Ui_SetupWizard()
    self.ui.setupUi(self)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.iso_dir          = None
    self.workspace_dir    = None
    self.eboot_path       = None
    self.terminology_path = None
    
    # Don't really feel like doing all this in Designer.
    self.connect(self.ui.btnIsoBrowse,          QtCore.SIGNAL("clicked()"), self.get_iso)
    self.connect(self.ui.btnIsoOK,              QtCore.SIGNAL("clicked()"), self.check_iso)
    self.connect(self.ui.btnWorkspaceBrowse,    QtCore.SIGNAL("clicked()"), self.get_workspace)
    self.connect(self.ui.btnWorkspaceOK,        QtCore.SIGNAL("clicked()"), self.check_workspace)
    self.connect(self.ui.btnEbootOK,            QtCore.SIGNAL("clicked()"), self.check_eboot)
    self.connect(self.ui.btnEbootSkip,          QtCore.SIGNAL("clicked()"), self.skip_eboot)
    self.connect(self.ui.btnSetupWorkspace,     QtCore.SIGNAL("clicked()"), self.setup_workspace)
    self.connect(self.ui.btnWorkspaceSkip,      QtCore.SIGNAL("clicked()"), self.skip_setup)
    self.connect(self.ui.btnCopyGfx,            QtCore.SIGNAL("clicked()"), self.copy_gfx)
    self.connect(self.ui.btnTerminologyNew,     QtCore.SIGNAL("clicked()"), self.create_terminology)
    self.connect(self.ui.btnTerminologyBrowse,  QtCore.SIGNAL("clicked()"), self.get_terminology)
    self.connect(self.ui.btnTerminologyOK,      QtCore.SIGNAL("clicked()"), self.check_terminology)
  
  def show_error(self, message):
    QtGui.QMessageBox.critical(self, "Error", message)
  
  def show_info(self, message):
    QtGui.QMessageBox.information(self, "Info", message)
    
  ##############################################################################
  ### STEP 1
  ##############################################################################
  def get_iso(self):
    dir = get_existing_dir(self, self.ui.txtIso.text())
    if not dir == "":
      self.ui.txtIso.setText(dir)
  
  def check_iso(self):
  
    iso_dir = common.qt_to_unicode(self.ui.txtIso.text(), normalize = False)
    if not os.path.isdir(iso_dir):
      self.show_error("ISO directory does not exist.")
      return
  
    validated = True
    with open("data/file_order.txt", "rb") as file_order:
      # Since we're reappropriating this from the file used by mkisofs,
      # we need to do a little bit of work on it to be useful here.
      # Split it up on the tab, take the first entry, and chop the slash
      # off the beginning so we can use it in os.path.join
      file_list = [line.split('\t')[0][1:] for line in file_order.readlines() if not line == ""]
      
      for filename in file_list:
        full_name = os.path.join(iso_dir, filename)
        if not os.path.isfile(full_name):
          validated = False
          self.show_error("%s missing from ISO directory." % full_name)
          break
    
    if not validated:
      return
    
    self.iso_dir = iso_dir
    self.show_info("ISO directory looks good.")
    self.ui.grpStep1.setEnabled(False)
    self.ui.grpStep2.setEnabled(True)
    
  ##############################################################################
  ### STEP 2
  ##############################################################################
  def get_workspace(self):
    dir = get_existing_dir(self, self.ui.txtWorkspace.text())
    if not dir == "":
      self.ui.txtWorkspace.setText(dir)
  
  def check_workspace(self):
    workspace_dir = common.qt_to_unicode(self.ui.txtWorkspace.text(), normalize = False)
    
    if not os.path.isdir(workspace_dir):
      try:
        os.makedirs(workspace_dir)
        self.show_info("Workspace directory created.")
      except:
        self.show_error("Error creating workspace directory.")
        return
    else:
      self.show_info("Workspace directory already exists.\n\nExisting data will be overwritten.")
    
    self.workspace_dir = workspace_dir
    self.ui.grpStep2.setEnabled(False)
    self.ui.grpStep3.setEnabled(True)
    
  ##############################################################################
  ### STEP 3 (UNUSED)
  ##############################################################################
  def check_eboot(self):
    eboot_path = os.path.join(self.workspace_dir, "EBOOT.BIN")
    if not os.path.isfile(eboot_path):
      self.show_error("EBOOT.BIN not found in workspace directory.")
      return
    
    eboot = ConstBitStream(filename = eboot_path)
    if not eboot[:32] == ConstBitStream(hex = "0x7F454C46"):
      self.show_error("EBOOT.BIN is encrypted.")
      return
    
    self.eboot_path = eboot_path
    self.show_info("EBOOT.BIN looks good.")

  def skip_eboot(self):
    
    answer = QtGui.QMessageBox.warning(
      self,
      "Skip Setup",
      "Are you sure you want to skip checking the EBOOT?\n\nYou should only do this if you are using this for the PC version only.",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    self.ui.grpStep3.setEnabled(False)
    self.ui.grpStep4.setEnabled(True)
    
  ##############################################################################
  ### STEP 4
  ##############################################################################
  def generate_directories(self):
    self.data00_dir       = os.path.join(self.workspace_dir, DATA00_DIR)
    self.data01_dir       = os.path.join(self.workspace_dir, DATA01_DIR)
    self.voice_dir        = os.path.join(self.workspace_dir, VOICE_DIR)
    self.changes_dir      = os.path.join(self.workspace_dir, CHANGES_DIR)
    self.backup_dir       = os.path.join(self.workspace_dir, BACKUP_DIR)
    self.edited_iso_dir   = os.path.join(self.workspace_dir, EDITED_ISO_DIR)
    
    self.editor_data_dir  = os.path.join(self.workspace_dir, EDITOR_DATA_DIR)
    
  def skip_setup(self):
    
    answer = QtGui.QMessageBox.warning(
      self,
      "Skip Setup",
      "Are you sure you want to skip setting up your workspace?\n\nYou should only do this if you already have a workspace generated by the setup wizard.",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    self.generate_directories()
    
    self.ui.grpStep4.setEnabled(False)
    self.ui.grpStep5.setEnabled(True)
  
  def setup_workspace(self):
    data00  = os.path.join(self.iso_dir, DATA00_CPK)
    data01  = os.path.join(self.iso_dir, DATA01_CPK)
    voice   = os.path.join(self.workspace_dir, VOICE_AWB)
    
    self.generate_directories()
    
    progress = QProgressDialog("", QtCore.QString(), 0, 11000, self)
    progress.setWindowTitle("Setting up workspace...")
    progress.setWindowModality(Qt.Qt.WindowModal)
    progress.setMinimumDuration(0)
    progress.setValue(0)
    progress.setAutoClose(False)
    progress.setAutoReset(False)
    
    progress.setLabelText("Creating directories...")
    
    # Do the easy stuff first.
    if not os.path.isdir(self.changes_dir):
      os.makedirs(self.changes_dir)
    progress.setValue(progress.value() + 1)
    
    if not os.path.isdir(self.backup_dir):
      os.makedirs(self.backup_dir)
    progress.setValue(progress.value() + 1)
    
    if not os.path.isdir(self.editor_data_dir):
      os.makedirs(self.editor_data_dir)
    progress.setValue(progress.value() + 1)
    
    thread_fns = [
      {"target": extract_cpk, "kwargs": {"filename": data00, "out_dir": self.data00_dir}},
      {"target": extract_cpk, "kwargs": {"filename": data01, "out_dir": self.data01_dir}},
    ]
    
    # Going to capture stdout because I don't feel like
    # rewriting the extract functions to play nice with GUI.
    stdout      = sys.stdout
    sys.stdout  = cStringIO.StringIO()
    
    for thread_fn in thread_fns:
      thread = threading.Thread(**thread_fn)
      thread.start()
      
      while thread.isAlive():
        thread.join(THREAD_TIMEOUT)
        
        output = [line for line in sys.stdout.getvalue().split('\n') if len(line) > 0]
        progress.setValue(progress.value() + len(output))
        if len(output) > 0:
          progress.setLabelText("Extracting %s..." % output[-1])
        
        sys.stdout = cStringIO.StringIO()
    
    sys.stdout = stdout
    
    # Give us an ISO directory for the editor to place modified files in.
    progress.setLabelText("Copying ISO files...")
    
    # ISO directory needs to not exist for copytree.
    if os.path.isdir(self.edited_iso_dir):
      shutil.rmtree(self.edited_iso_dir)
    
    # One more thing we want threaded so it doesn't lock up the GUI.
    thread = threading.Thread(target = shutil.copytree, kwargs = {"src": self.iso_dir, "dst": self.edited_iso_dir})
    thread.start()
    
    while thread.isAlive():
      thread.join(THREAD_TIMEOUT)
      progress.setLabelText("Copying ISO files...")
      # It has to increase by some amount or it won't update and the UI will lock up.
      progress.setValue(progress.value() + 1)
      
    # shutil.copytree(self.iso_dir, self.edited_iso_dir)
    progress.setValue(progress.value() + 1)
    
    # Files we want to make blank, because they're unnecessary.
    blank_files = [
      os.path.join(self.edited_iso_dir, "PSP_GAME", "INSDIR", "UMDIMAGE.DAT"),
      os.path.join(self.edited_iso_dir, "PSP_GAME", "SYSDIR", "UPDATE", "DATA.BIN"),
      os.path.join(self.edited_iso_dir, "PSP_GAME", "SYSDIR", "UPDATE", "EBOOT.BIN"),
      os.path.join(self.edited_iso_dir, "PSP_GAME", "SYSDIR", "UPDATE", "PARAM.SFO"),
    ]
    
    for blank in blank_files:
      with open(blank, "wb") as f:
        pass
    
    # NOTE: To re-enable this, Simply remove the hashtag before the codes.
    # Copy the decrypted EBOOT into the ISO folder and apply our hacks to it.
    # progress.setLabelText("Hacking EBOOT...")
    # progress.setValue(progress.value() + 1)
    
    # hacked_eboot = BitStream(filename = self.eboot_path)
    # hacked_eboot = apply_eboot_patches(hacked_eboot)
    # with open(os.path.join(self.edited_iso_dir, "PSP_GAME", "SYSDIR", "EBOOT.BIN"), "wb") as f:
      #hacked_eboot.tofile(f)
    # shutil.copy(self.eboot_path, os.path.join(self.edited_iso_dir, "PSP_GAME", "SYSDIR", "EBOOT.BIN"))
    
    progress.setLabelText("Extracting editor data...")
    progress.setValue(progress.value() + 1)
    
    # Extract the editor data.
    editor_data = zipfile.ZipFile("data/editor_data.zip", "r")
    editor_data.extractall(self.editor_data_dir)
    editor_data.close()
    
    progress.setValue(progress.maximum())
    progress.close()
    
    self.ui.grpStep4.setEnabled(False)
    self.ui.grpStep5.setEnabled(True)
    
  ##############################################################################
  ### STEP 5
  ##############################################################################
  def copy_gfx(self):
    gfx_dir = os.path.join(self.editor_data_dir, "gfx")
    
    if os.path.isdir(gfx_dir):
      shutil.rmtree(gfx_dir)
    
    os.makedirs(gfx_dir)
    
    progress = QProgressDialog("", "Abort", 0, 0, self)
    progress.setWindowTitle("Copying GFX...")
    progress.setWindowModality(Qt.Qt.WindowModal)
    progress.setMinimumDuration(0)
    progress.setValue(0)
    progress.setAutoClose(False)
    
    progress.setLabelText("Setting up GFX dir.")
    progress.setMaximum(5)
    progress.setValue(0)
    
    # Extract the images we can't just take directly from the game's data.
    gfx_bin = zipfile.ZipFile("data/gfx_base.zip", "r")
    progress.setValue(1)
    progress.setValue(2)
    gfx_bin.extractall(gfx_dir)
    progress.setValue(5)
    gfx_bin.close()
    
    # We can mostly loop this.
    gfx_data = [
      ("ammo",      "kotodama_icn_???.gim"),
      ("bgd",       "bgd_???.gim"),
      ("cutin",     "cutin_icn_???.gim"),
      ("events",    "gallery_icn_???.gim"),
      ("movies",    "bin_movie_gallery_l.pak/0000/000[1789].gim"),
      ("movies",    "bin_movie_gallery_l.pak/0000/00[123]?.gim"),
      ("movies",    "gallery_ico_m_none.gim"),
      ("movies",    "gallery_thumbnail_m_???.gim"),
      ("nametags",  "tex_system.pak/00[12]?.gim"),
      ("nametags",  "tex_system.pak/003[0123456].gim"),
      ("presents",  "present_icn_???.gim"),
      ("sprites",   "bustup_??_??.gim"),
      ("sprites",   "stand_??_??.gmo"),
    ]
    
    for (dir, file_glob) in gfx_data:
      out_dir = os.path.join(gfx_dir, dir)
      files   = glob.glob(os.path.join(self.data01_dir, file_glob))
      
      progress.setLabelText("Copying %s." % dir)
      progress.setMaximum(len(files))
      progress.setValue(0)
      
      if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
      
      for i, image in enumerate(files):
        if i % 10 == 0:
          progress.setValue(i)
        
        if progress.wasCanceled():
          return
        
        src  = image
        dest = os.path.join(out_dir, os.path.basename(src))
        shutil.copy(src, dest)
      
      progress.setValue(len(files))
    
    progress.setLabelText("Copying font.")
    progress.setMaximum(4)
    progress.setValue(0)
    
    # The font we have to get from umdimage2.
    font_dir = os.path.join(gfx_dir, "font")
    if not os.path.isdir(font_dir):
      os.makedirs(font_dir)
    
    progress.setValue(1)
    # And convert to PNG with an alpha channel so our editor can use it.
    font1 = font_bmp_to_alpha(os.path.join(self.data01_dir, "jp", "font", "font.pak", "0000.bmp"))
    progress.setValue(2)
    font2 = font_bmp_to_alpha(os.path.join(self.data01_dir, "jp", "font", "font.pak", "0002.bmp"))
    progress.setValue(3)
    
    font1.save(os.path.join(font_dir, "Font01.png"))
    font2.save(os.path.join(font_dir, "Font02.png"))
    shutil.copy(os.path.join(self.data01_dir, "jp", "font", "font.pak", "0001.font"), os.path.join(font_dir, "Font01.font"))
    shutil.copy(os.path.join(self.data01_dir, "jp", "font", "font.pak", "0003.font"), os.path.join(font_dir, "Font02.font"))
    
    progress.setValue(4)
    
    # And then the flash files. This'll be fun.
    flash_dir = os.path.join(gfx_dir, "flash")
    if not os.path.isdir(flash_dir):
      os.makedirs(flash_dir)

    #flash2_dir = os.path.join(gfx_dir, "flash2")
    #if not os.path.isdir(flash2_dir):
      #os.makedirs(flash2_dir)
    
     #Because there's so many in so many different places, I just stored a list
     #of the flash files we need in the gfx_base archive. So let's load that.
    with open(os.path.join(gfx_dir, "fla.txt"), "rb") as fla:
      fla_list = fla.readlines()
      
      progress.setLabelText("Copying flash.")
      progress.setMaximum(len(fla_list))
      progress.setValue(0)
      
      for i, flash in enumerate(fla_list):
        if i % 10 == 0:
          progress.setValue(i)
        
        if progress.wasCanceled():
          return
        
        flash = flash.strip()
        fla_name = flash[:7] # fla_###
        
        src  = os.path.join(self.data01_dir, "all", "flash", flash)
        dest = os.path.join(flash_dir, "%s.gim" % fla_name)

        shutil.copy(src, dest)
        
      progress.setValue(len(fla_list))
    
    # We have a couple sets of files that aren't named the way we want them to
    # be, just because of how they're stored in umdimage.
    progress.setLabelText("Renaming files.")
    to_rename = [
      ("movies",    "movie_%03d.gim", range(32)),
      ("nametags", "%02d.gim", range(23) + [24, 25, 30, 31]),
    ]
    
    for (folder, pattern, nums) in to_rename:
      folder  = os.path.join(gfx_dir, folder)
      files   = glob.glob(os.path.join(folder, "*.gim"))
      
      progress.setMaximum(len(files))
      progress.setValue(0)
      
      for i, image in enumerate(files):
        if i % 10 == 0:
          progress.setValue(i)
        
        if progress.wasCanceled():
          return
        
        src  = image
        dest = os.path.join(folder, pattern % nums[i])
        
        if os.path.isfile(dest):
          os.remove(dest)
        
        shutil.move(src, dest)
    
    sprite_dir = os.path.join(gfx_dir, "sprites")
    gmo_files = glob.glob(os.path.join(sprite_dir, "*.gmo"))
    
    progress.setLabelText("Extracting GMO files.")
    progress.setValue(0)
    progress.setMaximum(len(gmo_files))
    
    for i, gmo_file in enumerate(gmo_files):
      if i % 10 == 0:
        progress.setValue(i)
      
      if progress.wasCanceled():
        return
      
      name, ext = os.path.splitext(os.path.basename(gmo_file))
      gim_file  = os.path.join(sprite_dir, name + ".gim")
      
      gmo = GmoFile(filename = gmo_file)
      
      # Once we've loaded it, we're all done with it, so make it go away.
      os.remove(gmo_file)
      
      if gmo.gim_count() == 0:
        continue
      
      gim = gmo.get_gim(0)
      
      with open(gim_file, "wb") as f:
        gim.tofile(f)
    
    if self.ui.chkGimToPng.isChecked():
      gim_files = glob.glob(os.path.join(gfx_dir, "*", "*.gim"))
      
      progress.setLabelText("Converting GIM to PNG.")
      progress.setValue(0)
      progress.setMaximum(len(gim_files))
      
      converter = GimConverter()
      
      for i, gim_file in enumerate(gim_files):
        progress.setValue(i)
        if progress.wasCanceled():
          return
        
        converter.gim_to_png(gim_file)
        os.remove(gim_file)
    
    progress.close()
    
    self.gfx_dir = gfx_dir
    
    self.ui.grpStep5.setEnabled(False)
    self.ui.grpStep6.setEnabled(True)
    
  ##############################################################################
  ### STEP 6
  ##############################################################################
  def create_terminology(self):
    dir = get_save_file(self, self.ui.txtTerminology.text(), filter = "Terminology.csv (*.csv)")
    if not dir == "":
      self.ui.txtTerminology.setText(dir)
  
  def get_terminology(self):
    dir = get_open_file(self, self.ui.txtTerminology.text(), filter = "Terminology.csv (*.csv)")
    if not dir == "":
      self.ui.txtTerminology.setText(dir)
  
  def check_terminology(self):
    terms_file = common.qt_to_unicode(self.ui.txtTerminology.text(), normalize = False)
    
    if not terms_file:
      self.show_error("No terminology file provided.")
      return
    
    if not os.path.isfile(terms_file):
      # Create it.
      with open(terms_file, "wb") as f:
        self.show_info("Terminology file created.")
    
    self.terminology = terms_file
    
    self.ui.grpStep6.setEnabled(False)
    self.ui.btnFinish.setEnabled(True)
  
  ##############################################################################
  ### @fn   accept()
  ### @desc Overrides the OK button.
  ##############################################################################
  def accept(self):
    # Save typing~
    cfg = common.editor_config
    
    cfg.backup_dir    = self.backup_dir
    cfg.changes_dir   = self.changes_dir
    cfg.dupes_csv     = os.path.join(self.editor_data_dir, DUPES_CSV)
    cfg.gfx_dir       = self.gfx_dir
    cfg.iso_dir       = self.edited_iso_dir
    cfg.iso_file      = os.path.join(self.workspace_dir, EDITED_ISO_FILE)
    cfg.similarity_db = os.path.join(self.editor_data_dir, SIMILARITY_DB)
    cfg.terminology   = self.terminology
    cfg.data00_dir    = self.data00_dir
    cfg.data01_dir    = self.data01_dir
    cfg.voice_dir     = self.voice_dir
    
    common.editor_config = cfg
    common.editor_config.save_config()
    
    super(SetupWizard, self).accept()
  
  ##############################################################################
  ### @fn   reject()
  ### @desc Overrides the Cancel button.
  ##############################################################################
  def reject(self):
    super(SetupWizard, self).reject()

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = SetupWizard()
  form.show()
  sys.exit(app.exec_())

### EOF ###
