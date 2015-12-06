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
from ui.scriptdump import Ui_ScriptDumpMenu

import common
from dialog_fns import get_save_file
from object_labels import get_map_name
from script_dump import script_to_text
from script_map import SCRIPT_MAP
from tree import list_to_tree

class ScriptDumpMenu(QtGui.QDialog):
  def __init__(self, parent = None):
    super(ScriptDumpMenu, self).__init__(parent)
    
    self.ui = Ui_ScriptDumpMenu()
    self.ui.setupUi(self)
    #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.current_dir = None
    self.last_file   = ""
    
    self.updateUI()
    self.populate_list()
  
  ##############################################################################
  ### @fn   dump_script()
  ### @desc Dumps the selected folders to a text file.
  ##############################################################################
  def dump_script(self):
    to_dump = self.get_checked([self.ui.treeFileList.topLevelItem(i) for i in range(self.ui.treeFileList.topLevelItemCount())])
    
    if not to_dump:
      QtGui.QMessageBox.warning(self, "No Selection", "No folders have beens selected to dump.")
      return
    
    out_file = get_save_file(self, self.last_file, "Text files (*.txt)")
    if out_file == "":
      return
    
    translated    = not self.ui.chkUntranslated.isChecked()
    strip_clt     = self.ui.chkStripClt.isChecked()
    only_voiced   = self.ui.chkOnlyVoiced.isChecked()
    line_numbers  = self.ui.chkLineNumbers.isChecked()
    
    progress = QProgressDialog("Dumping...", QtCore.QString(), 0, len(to_dump), self)
    progress.setWindowTitle("Dumping...")
    progress.setWindowModality(Qt.Qt.WindowModal)
    progress.setValue(0)
    progress.setAutoClose(False)
    progress.setMinimumDuration(0)
    
    # print out_file
    with open(out_file, "wb") as f:
      for dir in to_dump:
        progress.setLabelText("Dumping %s..." % dir)
        f.write(script_to_text(dir, translated, strip_clt, only_voiced, line_numbers).encode("UTF-8"))
        progress.setValue(progress.value() + 1)
    
    progress.close()
    
    self.last_file = out_file
  
  def get_checked(self, items):
    checked = []
    
    for item in items:
      if item.childCount() == 0 and item.checkState(0) == Qt.Qt.Checked:
        checked.append(common.qt_to_unicode(item.text(0)))
      else:
        checked.extend(self.get_checked([item.child(i) for i in range(item.childCount())]))
    
    return checked
  
  ##############################################################################
  ### @fn   populate_list()
  ### @desc Displays the list of folders which can be opened.
  ##############################################################################
  def populate_list(self):
    
    self.ui.treeFileList.clear()
    
    tree_items = list_to_tree(SCRIPT_MAP)
    
    for item in tree_items:
      if item.text(0) == "EBOOT Text":
        continue
    
      # We want check boxes here, but for them to show up,
      # we actually have to set the state to ~something~.
      # So recursively set everything to unchecked, then add it.
      item.setCheckState(0, Qt.Qt.Unchecked)
      self.recursiveChecks(item)
      
      self.ui.treeFileList.addTopLevelItem(item)
  
  ##############################################################################
  ### @fn   changeSelection()
  ### @desc Triggered when the user selects something in the tree.
  ###       If we've hit a leaf node, store the folder.
  ##############################################################################
  def changeSelection(self, current, prev):
  
    if current.childCount() == 0:
      self.current_dir = common.qt_to_unicode(current.text(0))
    else:
      self.current_dir = None
      
    self.updateUI()
  
  ##############################################################################
  ### @fn   updateChecks()
  ### @desc Triggered when the user changes something in the tree.
  ###       Recursively set the state of this item's children's check boxes.
  ###       From http://stackoverflow.com/a/9203523
  ##############################################################################
  def updateChecks(self, item, column):
    if not column == 0:
      return
    self.recursiveChecks(item)
  
  def recursiveChecks(self, parent):
    state = parent.checkState(0)
    for i in range(parent.childCount()):
      parent.child(i).setCheckState(0, state)
      self.recursiveChecks(parent.child(i))
  
  ##############################################################################
  ### @fn   updateUI()
  ### @desc Updates info about the selected file.
  ##############################################################################
  def updateUI(self):
  
    if not self.current_dir == None:
      chapter, scene, room, mode = common.get_dir_info(self.current_dir)
      
      self.ui.lblChapter.setText(common.chapter_to_text(chapter))
      
      if not scene == -1:
        self.ui.lblScene.setText("%03d" % scene)
      else:
        self.ui.lblScene.setText("N/A")
      
      if not room == -1:
        self.ui.lblRoom.setText("%03d: %s" % (room, get_map_name(room)))
      else:
        self.ui.lblRoom.setText("N/A")
      
      self.ui.lblMode.setText(common.mode_to_text(mode))
    
    else:
      self.ui.lblChapter.setText("N/A")
      self.ui.lblScene.setText("N/A")
      self.ui.lblRoom.setText("N/A")
      self.ui.lblMode.setText("N/A")
  
  ##############################################################################
  ### @fn   doubleClicked()
  ### @desc Triggered when the user double-clicks on an item in the tree.
  ##############################################################################
  def doubleClicked(self, item, column):
    pass

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = ScriptDumpMenu()
  form.show()
  sys.exit(app.exec_())

### EOF ###