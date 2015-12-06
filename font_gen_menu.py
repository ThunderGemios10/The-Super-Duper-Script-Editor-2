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

from PyQt4 import Qt, QtGui, QtCore
from PyQt4.QtGui import QProgressDialog
from ui.fontgenerator import Ui_FontGenerator

try:
  import cPickle as pickle
except:
  import pickle

from enum import Enum
import logging
import os
import shutil
import tempfile
import threading
import time

import common
import font_generator
import text_printer

from backup import backup_files
from dialog_fns import get_save_file, get_open_file
from font_gen_settings import FontSettings, FONT1, FONT2
from font_gen_widget import FontGenWidget

FONT_EXTENSION = ".sdse-font"
THREAD_TIMEOUT = 0.1

REQUIRED_CHARS = [
  u'\u2261', # The default character the game uses in case something's missing.
  u'.',      # Needed for the hacked version of the ammo/present menu.
  u'…',      # Needed for the original version of the ammo/present menu.
  u'?',      # Needed for names of unknown items/extras/etc.
  u'？',     # Same.
]

class FontGenMenu(QtGui.QDialog):
  def __init__(self, parent=None):
    super(FontGenMenu, self).__init__(parent)
    
    self.ui = Ui_FontGenerator()
    self.ui.setupUi(self)
    # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.ui.tabFonts.tabBar().tabMoved.connect(self.export_changed)
    
    self.filename = None
    self.loading = False
    
    self.load_last()
  
  def set_title(self):
    title = "Font Generator - %s[*]"
    if self.filename == None:
      title = title % "untitled"
    else:
      title = title % self.filename
    
    self.setWindowTitle(title)
  
  def ask_unsaved(self):
    if not self.isWindowModified():
      return True
    
    answer = QtGui.QMessageBox.question(
      self,
      "Unsaved Changes",
      "Would you like to save your changes?",
      buttons = QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel,
      defaultButton = QtGui.QMessageBox.Cancel
    )
    
    if answer == QtGui.QMessageBox.Cancel:
      return False
    elif answer == QtGui.QMessageBox.Discard:
      return True
    elif answer == QtGui.QMessageBox.Save:
      self.save(filename = self.filename)
      return True
  
  def update_config(self):
    common.editor_config.last_font = self.filename
    common.editor_config.save_config()
  
  ##############################################################################
  ### NEW FUNCTIONS
  ##############################################################################
  def new(self):
    self.filename = None
    self.set_title()
    
    self.ui.tabFonts.clear()
    self.add_tab()
    
    self.setWindowModified(False)
  
  def new_clicked(self):
    if not self.ask_unsaved():
      return
    
    self.new()
  
  ##############################################################################
  ### SAVE FUNCTIONS
  ##############################################################################
  def save(self, filename = None):
    if not filename:
      # Ask for a filename.
      filename = get_save_file(self, os.path.dirname(common.editor_config.last_font), filter = "SDSE font files (*.sdse-font)")
    
      # And if that failed...
      if not filename:
        return False
    
    # Save shit.
    font_settings = FontSettings()
    
    font_settings.font_data       = self.get_font_data()
    font_settings.gen_for_game    = self.ui.chkGenForGame.isChecked()
    font_settings.gen_for_editor  = self.ui.chkGenForEditor.isChecked()
    font_settings.left_to_right   = self.ui.rdoLeftToRight.isChecked()
    if self.ui.rdoGenFont1.isChecked():
      font_settings.font_type = FONT1
    else:
      font_settings.font_type = FONT2
    
    with open(filename, "wb") as f:
      pickle.dump(font_settings, f, pickle.HIGHEST_PROTOCOL)
    
    self.filename = filename
    self.set_title()
    self.setWindowModified(False)
    
    self.update_config()
  
  def save_clicked(self):
    self.save(filename = self.filename)
  
  def save_as_clicked(self):
    self.save(filename = None)
  
  ##############################################################################
  ### LOAD FUNCTIONS
  ##############################################################################
  def load(self, filename = None):
    if not filename or not os.path.isfile(filename):
      # Ask for a filename.
      filename = get_open_file(self, os.path.dirname(common.editor_config.last_font), filter = "SDSE font files (*.sdse-font)")
    
      # And if that failed...
      if not filename or not os.path.isfile(filename):
        return False
    
    self.loading = True
    
    # Load shit.
    with open(filename, "rb") as f:
      try:
        temp_settings = pickle.load(f)
      except:
        return False
    
    # In case we're coming from pickled data that might
    # not have all the members we need.
    font_settings = FontSettings()
    font_settings.__dict__.update(temp_settings.__dict__)
    
    self.ui.tabFonts.clear()
    
    for font_data in font_settings.font_data:
      tab = self.add_tab()
      self.ui.tabFonts.widget(tab).import_data(font_data)
    
    self.ui.chkGenForGame.setChecked(font_settings.gen_for_game)
    self.ui.chkGenForEditor.setChecked(font_settings.gen_for_editor)
    
    if font_settings.font_type == FONT1:
      self.ui.rdoGenFont1.setChecked(True)
      self.ui.rdoGenFont2.setChecked(False)
    else:
      self.ui.rdoGenFont1.setChecked(False)
      self.ui.rdoGenFont2.setChecked(True)
    
    if font_settings.left_to_right:
      self.ui.rdoLeftToRight.setChecked(True)
      self.ui.rdoRightToLeft.setChecked(False)
    else:
      self.ui.rdoLeftToRight.setChecked(False)
      self.ui.rdoRightToLeft.setChecked(True)
    
    self.filename = filename
    self.set_title()
    self.setWindowModified(False)
    
    self.update_config()
    
    self.loading = False
  
  def load_last(self):
    last_font = common.editor_config.last_font
    
    if os.path.isfile(last_font):
      self.load(filename = last_font)
    else:
      self.new()
  
  def load_clicked(self):
    if not self.ask_unsaved():
      return
    
    self.load()
  
  ##############################################################################
  ### TAB FUNCTIONS
  ##############################################################################
  def __tab_title(self, widget):
    return "%s [%d]" % (widget.font_name(), widget.font_size())
  
  @QtCore.pyqtSlot()
  def tab_modified(self):
    widget = self.sender()
    tab = self.ui.tabFonts.indexOf(widget)
    tab_title = self.__tab_title(widget)
    self.ui.tabFonts.setTabText(tab, tab_title)
    
    if not self.loading:
      self.setWindowModified(True)
  
  def add_tab(self):
    font_widget = FontGenWidget()
    font_widget.font_type = self.font_type()
    font_widget.modified.connect(self.tab_modified)
    tab = self.ui.tabFonts.addTab(font_widget, self.__tab_title(font_widget))
    
    if not self.loading:
      self.setWindowModified(True)
    
    return tab
  
  def remove_tab(self):
    answer = QtGui.QMessageBox.warning(
      self,
      "Remove Tab",
      "Are you sure you want to remove this tab?\n\n" +
      "This action cannot be undone. Proceed?",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    widget = self.ui.tabFonts.currentWidget()
    self.ui.tabFonts.removeTab(self.ui.tabFonts.currentIndex())
    del widget
    
    self.setWindowModified(True)
  
  ##############################################################################
  ### FONT GENERATION
  ##############################################################################
  def get_font_data(self):
    font_data = []
    
    for i in range(self.ui.tabFonts.count()):
      data = self.ui.tabFonts.widget(i).get_data()
      font_data.append(data)
    
    return font_data
  
  def generate_font(self):
    progress = QProgressDialog("", QtCore.QString(), 0, 0, self)
    progress.setWindowModality(Qt.Qt.WindowModal)
    progress.setWindowTitle("Generating font...")
    progress.setLabelText("Generating font...")
    progress.setMinimumDuration(0)
    progress.setAutoClose(False)
    
    # Thread this because it's slow as hell and we don't want to lock up the GUI.
    thread = threading.Thread(target = self.__generate_font__)
    thread.start()
    
    while thread.isAlive():
      thread.join(THREAD_TIMEOUT)
      # It has to change by some amount or it won't update and the UI will lock up.
      progress.setValue(progress.value() - 1)
    
    progress.close()
    
  def __generate_font__(self):
    gen_font1   = self.ui.rdoGenFont1.isChecked()
    temp_dir    = tempfile.mkdtemp(prefix = "sdse-")
    temp_name   = "font"
    font_type   = font_generator.FONT_TYPES.font01 if gen_font1 else font_generator.FONT_TYPES.font02
    for_game    = self.ui.chkGenForGame.isChecked()
    for_editor  = self.ui.chkGenForEditor.isChecked()
    
    font_data = self.get_font_data()
    if self.ui.rdoRightToLeft.isChecked():
      font_data.reverse()
    
    # Add the required characters to the end of the lowest-priority font
    # so they're there by default but they don't override any existing
    # settings for them, if they're already there.
    font_data[-1].chars += ''.join(REQUIRED_CHARS)
    
    font = font_generator.gen_font(font_data, font_type = font_type, img_width = 1024, draw_outlines = False)
    font.save(temp_dir, temp_name, for_game, for_editor, font_type, game = font_generator.GAMES.sdr2)
    
    basename  = os.path.join(temp_dir, temp_name)
    font_png  = basename + ".png"
    font_bmp  = basename + ".bmp"
    font_font = basename + ".font"
    
    font_dir  = os.path.join(common.editor_config.data01_dir, "jp", "font", "font.pak")
    
    if for_game:
      game_bmp  = "0000.bmp"  if gen_font1 else "0002.bmp"
      game_font = "0001.font" if gen_font1 else "0003.font"
      
      backup_files(font_dir, [game_bmp, game_font], suffix = "_FONT")
      # backup_time = time.strftime("%Y.%m.%d_%H.%M.%S_FONT")
      # backup_dir = os.path.join(common.editor_config.backup_dir, backup_time, "font.pak")
      # if not os.path.isdir(backup_dir):
        # os.makedirs(backup_dir)
      
      # Copy our existing data into the backup directory.
      # shutil.copy(game_bmp, backup_dir)
      # shutil.copy(game_font, backup_dir)
      
      # Then replace it with the one we generated.
      shutil.copy(font_bmp, os.path.join(font_dir, game_bmp))
      shutil.copy(font_font, os.path.join(font_dir, game_font))
    
    if for_editor:
      editor_png  = os.path.join(common.editor_config.gfx_dir, "font", "Font01.png"  if gen_font1 else "Font02.png")
      editor_font = os.path.join(common.editor_config.gfx_dir, "font", "Font01.font" if gen_font1 else "Font02.font")
      
      # Copy our files in.
      shutil.copy(font_png, editor_png)
      shutil.copy(font_font, editor_font)
      
      # Reparse the font for the editor.
      text_printer.load_fonts()
    
    shutil.rmtree(temp_dir)
  
  ##############################################################################
  ### MISC FUNCTIONS
  ##############################################################################
  def font_type(self):
    return font_generator.FONT_TYPES.font01 if self.ui.rdoGenFont1.isChecked() else font_generator.FONT_TYPES.font02
  
  def export_changed(self):
    font_type = self.font_type()
    for i in range(self.ui.tabFonts.count()):
      self.ui.tabFonts.widget(i).font_type = font_type
      self.ui.tabFonts.widget(i).auto_update()
      
    if not self.loading:
      self.setWindowModified(True)
  
  ##############################################################################
  ### @fn   accept()
  ### @desc Overrides the OK button.
  ##############################################################################
  def accept(self):
    if not self.ask_unsaved():
      return
    
    super(FontGenMenu, self).accept()
  
  ##############################################################################
  ### @fn   reject()
  ### @desc Overrides the cancel button.
  ##############################################################################
  def reject(self):
    if not self.ask_unsaved():
      return
    
    super(FontGenMenu, self).reject()

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = FontGenMenu()
  form.show()
  sys.exit(app.exec_())

### EOF ###