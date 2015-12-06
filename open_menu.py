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
from PyQt4.QtGui import QColor, QPalette
from ui.openmenu import Ui_OpenMenu

import common
import object_labels
import script_map
import tree

class OpenMenu(QtGui.QDialog):
  def __init__(self, parent = None, start_dir = ""):
    super(OpenMenu, self).__init__(parent)
    
    self.ui = Ui_OpenMenu()
    self.ui.setupUi(self)
    #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.current_dir = None
    self.current_node = None
    self.updateUI()
    self.populate_list()
    
    self.normal_palette = self.ui.txtSearch.palette()
    self.red_palette    = QPalette(self.normal_palette)
    self.red_palette.setColor( QPalette.Normal, QPalette.Base, QColor(200, 98, 96) )
    
    self.findDirectory(start_dir)
  
  ##############################################################################
  ### @fn   populate_list()
  ### @desc Displays the list of folders which can be opened.
  ##############################################################################
  def populate_list(self):
    
    self.ui.treeFileList.clear()
    
    reload(script_map)
    tree_items = tree.list_to_tree(script_map.SCRIPT_MAP)
    
    for item in tree_items:
      self.ui.treeFileList.addTopLevelItem(item)
  
  def refresh_list(self):
    directory = self.current_dir
    self.populate_list()
    self.findDirectory(directory)
  
  ##############################################################################
  ### @fn   changeSelection()
  ### @desc Triggered when the user selects something in the tree.
  ###       If we've hit a leaf node, store the folder.
  ##############################################################################
  def changeSelection(self, current, prev):
  
    if current and current.childCount() == 0:
      self.current_dir = common.qt_to_unicode(current.text(0))
    else:
      self.current_dir = None
      
    self.updateUI()
  
  ##############################################################################
  ### @fn   updateUI()
  ### @desc Updates info about the selected file.
  ##############################################################################
  def updateUI(self):
  
    if not self.current_dir == None:
      chapter, scene, room, mode = common.get_dir_info(self.current_dir)
      
      self.ui.lblChapter.setText(common.chapter_to_text(chapter))
      
      if not scene == -1:
        if chapter == common.CHAPTER_FREETIME:
          self.ui.lblScene.setText("%03d: %s" % (scene, object_labels.get_char_name(scene, common.editor_config.data01_dir)))
        elif chapter == common.CHAPTER_ISLAND and scene >= 701 and scene <= 715:
          scene -= 700
          self.ui.lblScene.setText("%03d: %s" % (scene, object_labels.get_char_name(scene, common.editor_config.data01_dir)))
        else:
          self.ui.lblScene.setText("%03d" % scene)
      else:
        self.ui.lblScene.setText("N/A")
      
      if not room == -1:
        self.ui.lblRoom.setText("%03d: %s" % (room, object_labels.get_map_name(room, common.editor_config.data01_dir)))
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
    if item.childCount() == 0:
      self.changeSelection(item, None)
      self.accept()
  
  ##############################################################################
  ### @fn   findDirectory()
  ### @desc Triggered on startup or by editing the search box.
  ##############################################################################
  def findDirectory(self, directory):
    
    if directory:
      nodes = self.ui.treeFileList.findItems(directory, Qt.Qt.MatchContains | Qt.Qt.MatchRecursive)
      
      if len(nodes) >= 1:
        self.ui.treeFileList.setCurrentItem(nodes[0])
        self.ui.treeFileList.scrollToItem(nodes[0], QtGui.QAbstractItemView.PositionAtCenter)
        
        self.ui.txtSearch.setPalette(self.normal_palette)
      else:
        self.ui.txtSearch.setPalette(self.red_palette)
  
  ##############################################################################
  ### @fn   accept()
  ### @desc Overrides the OK button to make sure a folder is selected.
  ##############################################################################
  def accept(self):
    if self.current_dir == None:
      QtGui.QMessageBox.critical(self, "No Selection", "Please select a script folder.")
      return
    super(OpenMenu, self).accept()
  
  ##############################################################################
  ### @fn   reject()
  ### @desc Overrides the Cancel button.
  ##############################################################################
  def reject(self):
    self.current_dir = None
    super(OpenMenu, self).reject()

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = OpenMenu()
  form.show()
  sys.exit(app.exec_())

### EOF ###