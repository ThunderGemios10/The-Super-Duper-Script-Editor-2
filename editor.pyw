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
from PyQt4.QtGui import QMessageBox

import logging
import os
import sys

LOG_FILE = "data/debug.log"
LOG_FMT  = "\n%(asctime)s: %(message)s"
logging.basicConfig(filename = LOG_FILE, level = logging.DEBUG, format = LOG_FMT)

try:
  import common
  from settings_menu import SettingsMenu
  from setup_wizard import SetupWizard
except:
  logging.exception('Exception importing.')
  raise

def check_config():
  msg_box = QMessageBox()
  msg_box.setWindowTitle("Config Error")
  msg_box.setTextFormat(Qt.Qt.RichText)
  msg_box.setText("<p>Couldn't find some of the files or directories needed by the editor.</p><p>If this is your first time running the editor, you should run the setup wizard and create a workspace. If you already have a workspace (created <strong>by this editor</strong>, not any other tools), then just go to the settings menu and make sure everything's correct.</p><p>What would you like to do?</p>")
  msg_box.setIcon(QMessageBox.Warning)
  wizard_btn = msg_box.addButton("Run the setup wizard", QMessageBox.AcceptRole)
  config_btn = msg_box.addButton("Show the settings menu", QMessageBox.AcceptRole)
  exit_btn   = msg_box.addButton("Exit", QMessageBox.RejectRole)
  msg_box.setEscapeButton(exit_btn)
  
  show_menu = False
  
  # Save typing~
  cfg = common.editor_config
  
  if not os.path.isfile(cfg.dupes_csv) or \
     not os.path.isdir (cfg.gfx_dir) or \
     not os.path.isdir (cfg.iso_dir) or \
     not os.path.isfile(cfg.similarity_db) or \
     not os.path.isfile(cfg.terminology) or \
     not os.path.isdir (cfg.data01_dir) or \
     not os.path.isdir (cfg.voice_dir):
    show_menu = True
  
  if show_menu:
    
    msg_box.exec_()
    answer = msg_box.clickedButton()
    
    if answer == wizard_btn:
      wizard = SetupWizard()
      wizard.exec_()
    
    elif answer == config_btn:
      menu = SettingsMenu()
      menu.exec_()
    
    return False
  
  return True

if __name__ == '__main__':

  try:
    app = QtGui.QApplication(sys.argv)
    
    if not check_config():
      sys.exit()
    
    from editor_form import EditorForm
    editor = EditorForm()
    
    desktop = app.desktop()
    
    desk_w = desktop.screenGeometry().width()
    desk_h = desktop.screenGeometry().height()
    form_w = editor.geometry().width()
    form_h = editor.geometry().height()
    
    x = (desk_w - form_w) / 2
    y = (desk_h - form_h) / 2
    
    editor.move(x, y)
    editor.show()
    
    sys.exit(app.exec_())
  
  except:
    logging.exception('Exception on editor.pyw')
    raise

##### EOF #####