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
from PyQt4.QtGui import QProgressDialog, QApplication, QTextCharFormat, QColor, QTextCursor
from PyQt4.QtCore import pyqtSignal

from ui.diffs import Ui_Diffs

import os
import re
import dir_tools
import text_files
import tree

import common

from list_files import list_all_files
from script_file import ScriptFile

from diff_match_patch import diff_match_patch

RE_SCRIPT  = re.compile(ur"(.*?)\0.*", re.UNICODE | re.S)
DIFFER = diff_match_patch()

def load_text(filename):
  text = text_files.load_text(filename)
  text = RE_SCRIPT.sub(u"\g<1>", text)
  return text

def parse_diffs(diffs):
  len1 = 0
  len2 = 0
  
  highlight1 = []
  highlight2 = []
  
  for op, data in diffs:
    if op == diff_match_patch.DIFF_EQUAL:
      len1 += len(data)
      len2 += len(data)
    
    elif op == diff_match_patch.DIFF_INSERT:
      highlight2.append((len2, len(data)))
      len2 += len(data)
    
    elif op == diff_match_patch.DIFF_DELETE:
      highlight1.append((len1, len(data)))
      len1 += len(data)
  
  return highlight1, highlight2

class DiffsMenu(QtGui.QDialog):
  def __init__(self, parent = None):
    super(DiffsMenu, self).__init__(parent)
    
    self.ui = Ui_Diffs()
    self.ui.setupUi(self)
    
    self.ui.actionCopyPath = QtGui.QAction("Copy path", None, triggered = self.copyPath)
    self.ui.treeResults.addAction(self.ui.actionCopyPath)
    
    self.folder1        = None
    self.folder2        = None
    self.files          = None
    self.files_nodupes  = None
    self.files_missing  = None
    
    self.saved_diffs    = {}
    
    self.format1 = QTextCharFormat()
    self.format1.setBackground(QColor(255, 224, 224))
    
    self.format2 = QTextCharFormat()
    self.format2.setBackground(QColor(224, 240, 255))
    
    self.menu_name = "Diffs"
    
    self.format_plain = QTextCharFormat()
  
  ##############################################################################
  ### @fn   copyPath()
  ### @desc Copies the path of the selected node to the clipboard.
  ##############################################################################
  def copyPath(self):
    node = self.ui.treeResults.currentItem()
    
    if not node == None:
      text = "{%s}" % tree.tree_item_to_path(node)
      
      clipboard = QApplication.clipboard()
      clipboard.setText(text)
  
  ##############################################################################
  ### @fn   set_folders()
  ### @desc Set the two folders to be compared.
  ##############################################################################
  def set_folders(self, folder1, folder2, files = None):
    if files == None:
      files1 = list_all_files(folder1)
      files2 = list_all_files(folder2)
      
      files = set()
      
      # Get rid of our folder paths so we're working on generic filenames
      # that can be used with either folder.
      files.update([file[len(folder1) + 1:] for file in files1 if file[-4:] == ".txt"])
      files.update([file[len(folder2) + 1:] for file in files2 if file[-4:] == ".txt"])
    
    self.ui.lblDir1.setText(folder1)
    self.ui.lblDir2.setText(folder2)
    
    self.folder1        = folder1
    self.folder2        = folder2
    self.files          = set(files)
    self.files_nodupes  = None
    self.files_missing  = None
    
    self.saved_diffs    = {}
    
    self.show_files()
  
  ##############################################################################
  ### @fn   show_files()
  ### @desc Shows the list of files.
  ##############################################################################
  def show_files(self):
  
    # If we're not showing identical files, then go through the list
    # and find and remove everything we don't want to see.
    if not self.ui.chkShowSame.isChecked():
      if self.files_nodupes == None:
        self.files_nodupes = set()
      
        for file in self.files:
          file1 = os.path.join(self.folder1, file)
          file2 = os.path.join(self.folder2, file)
          
          if not os.path.isfile(file1) or not os.path.isfile(file2):
            self.files_nodupes.add(file)
            continue
          
          text1 = text_files.load_text(file1)
          text2 = text_files.load_text(file2)
          
          if not text1 == text2:
            self.files_nodupes.add(file)
            
      files = self.files_nodupes
      
    else:
      files = self.files
      
    # If we're not showing files not present in both directories,
    # go through the list and strip them out.
    if not self.ui.chkNotBoth.isChecked():
      if self.files_missing == None:
        self.files_missing = set()
      
        for file in self.files:
          file1 = os.path.join(self.folder1, file)
          file2 = os.path.join(self.folder2, file)
          
          if not os.path.isfile(file1) or not os.path.isfile(file2):
            self.files_missing.add(file)
            
      files = files - self.files_missing
      
    self.ui.treeResults.clear()
    self.ui.treeResults.setHeaderLabel("Results (%d)" % len(files))
    
    if len(files) > 0:
      tree_items = []
      
      for file in files:
        file = os.path.normpath(file)
        file = dir_tools.consolidate_dir(file)
        tree_item = tree.path_to_tree(file)
        tree_items.append(tree_item)
      
      tree_items = tree.consolidate_tree_items(tree_items)
      
      for item in tree_items:
        self.ui.treeResults.addTopLevelItem(item)
      
      self.ui.treeResults.expandAll()
  
  ##############################################################################
  ### @fn   changedSelection()
  ### @desc Triggered when the user selects something in the tree.
  ##############################################################################
  def changedSelection(self, current, prev):
    if current == None or current.childCount() != 0:
      return
    
    file = common.qt_to_unicode(current.text(0))
    path = tree.tree_item_to_path(current.parent())
    self.setWindowTitle("%s - %s" % (self.menu_name, os.path.join(path, file)))
    path = dir_tools.expand_dir(path)
    
    file = os.path.join(path, file)
    file1 = os.path.join(self.folder1, file)
    file2 = os.path.join(self.folder2, file)
    
    if not os.path.isfile(file1):
      script1 = ScriptFile()
    else:
      script1 = ScriptFile(file1)
    
    if not os.path.isfile(file2):
      script2 = ScriptFile()
    else:
      script2 = ScriptFile(file2)
    
    # So we can loop this shit.
    to_diff = [
      # Text 1              Text 2              Text Box 1              Text Box 2
      (script1[common.editor_config.lang_trans],  script2[common.editor_config.lang_trans], self.ui.txtTranslated1, self.ui.txtTranslated2),
      (script1[common.editor_config.lang_orig],    script2[common.editor_config.lang_orig],   self.ui.txtOriginal1,   self.ui.txtOriginal2),
      (script1.comments,    script2.comments,   self.ui.txtComments1,   self.ui.txtComments2),
    ]
    
    # Save us a little bit of time recalculating.
    if file in self.saved_diffs:
      diffs = self.saved_diffs[file]
    else:
      diffs = [None] * len(to_diff)
    
    for i, (text1, text2, box1, box2) in enumerate(to_diff):
    
      if diffs[i] == None:
        diffs[i] = DIFFER.diff_main(text1, text2)
        DIFFER.diff_cleanupSemantic(diffs[i])
      
      box1.setPlainText(text1)
      box2.setPlainText(text2)
      
      highlight1, highlight2 = parse_diffs(diffs[i])
      
      cursor1 = box1.textCursor()
      cursor2 = box2.textCursor()
      
      cursor1.select(QTextCursor.Document)
      cursor2.select(QTextCursor.Document)
      cursor1.setCharFormat(self.format_plain)
      cursor2.setCharFormat(self.format_plain)
      
      cursor1.movePosition(QTextCursor.Start)
      cursor2.movePosition(QTextCursor.Start)
      
      for pos, length in highlight1:
        cursor1.setPosition(pos, QTextCursor.MoveAnchor)
        cursor1.setPosition(pos + length, QTextCursor.KeepAnchor)
        cursor1.setCharFormat(self.format1)
      
      cursor1.movePosition(QTextCursor.Start)
      
      for pos, length in highlight2:
        cursor2.setPosition(pos, QTextCursor.MoveAnchor)
        cursor2.setPosition(pos + length, QTextCursor.KeepAnchor)
        cursor2.setCharFormat(self.format2)
      
      cursor2.movePosition(QTextCursor.Start)
      
      box1.setTextCursor(cursor1)
      box2.setTextCursor(cursor2)
    
    # for i, (text1, text2, box1, box2) in enumerate(to_diff):
    self.saved_diffs[file] = diffs

if __name__ == "__main__":

  # folder1 = "Y:\\Danganronpa\\Danganronpa_BEST\\umdimage"
  folder1 = "Y:\\Danganronpa\\Danganronpa_BEST\\!changes"
  # folder1 = "Y:\\Dropbox\\Danganronpa\\Best\\bdh-umdimage_test-phase2"
  folder2 = "Y:\\Dropbox\\Danganronpa\\Best\\rito-umdimage_misc2"
  
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = DiffsMenu()
  form.set_folders(folder1, folder2)
  form.show()
  sys.exit(app.exec_())

### EOF ###