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
from PyQt4.QtGui import QProgressDialog, QShortcut, QKeySequence, \
                        QTextCursor, QTextEdit, QColor, QApplication
from PyQt4.QtCore import pyqtSignal

from ui.searchmenu import Ui_SearchMenu

import os.path
import re
import time

import common
import dir_tools
from list_files import list_all_files
import script_analytics
from script_file import ScriptFile
from text_files import load_text
import tree

class SearchMenu(QtGui.QDialog):
  ### SIGNALS ###
  open_clicked = pyqtSignal()
  
  def __init__(self, parent=None):
    super(SearchMenu, self).__init__(parent)
    
    self.ui = Ui_SearchMenu()
    self.ui.setupUi(self)
    
    self.ui.shortcutFind = QShortcut(QKeySequence("Ctrl+F"), self)
    self.ui.shortcutFind.activated.connect(self.select_query)
    
    self.ui.txtQuery.setCompleter(None)
    self.ui.txtQuery.setMaxCount(25)
    self.ui.txtQuery.setMaxVisibleItems(25)
    self.ui.txtQuery.setInsertPolicy(QtGui.QComboBox.NoInsert)
    self.ui.txtQuery.view().setTextElideMode(Qt.Qt.ElideNone)
    self.ui.txtQuery.currentIndexChanged.connect(self.select_query)
    
    self.ui.btnFilterSelAll.clicked.connect(lambda: self.filterSetAll(True))
    self.ui.btnFilterSelNone.clicked.connect(lambda: self.filterSetAll(False))
    
    # Unchecked is easier to work with,
    # since it searches everything if nothing's given.
    self.filterSetAll(False)
    
    self.ui.treeResults.setHeaderLabel("Results (0)")
    
    self.ui.actionCopyPath = QtGui.QAction("Copy path", None, triggered = self.copyPath)
    self.ui.treeResults.addAction(self.ui.actionCopyPath)
    
    self.query_re = None
    self.re_flags = re.UNICODE | re.MULTILINE
  
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
  ### @fn   search()
  ### @desc Commences a search.
  ##############################################################################
  def search(self):
    query = common.qt_to_unicode(self.ui.txtQuery.currentText())
    
    self.ui.txtQuery.removeItem(self.ui.txtQuery.findText(query))
    self.ui.txtQuery.insertItem(0, query)
    self.ui.txtQuery.setCurrentIndex(0)
    
    dir = common.editor_config.data01_dir
    
    if query == "":
      results = []
    else:
      results = self.search_bar(query)
      
    self.ui.treeResults.clear()
    self.ui.treeResults.setHeaderLabel("Results (%d)" % len(results))
    
    if len(results) > 0:
      tree_items = []
      
      for file in results:
        file = os.path.normpath(file)
        file = dir_tools.consolidate_dir(file)
        tree_item = tree.path_to_tree(file)
        tree_items.append(tree_item)
      
      tree_items = tree.consolidate_tree_items(tree_items)
      
      for item in tree_items:
        self.ui.treeResults.addTopLevelItem(item)
      
      self.ui.treeResults.expandAll()
    
    self.ui.txtOriginal.clear()
    self.ui.txtTranslated.clear()
    self.ui.txtComments.clear()
    
    self.update_highlights()
  
  ##############################################################################
  ### @fn   search_bar()
  ### @desc Search while displaying a progress bar.
  ##############################################################################
  def search_bar(self, query):
    matches = []
    
    progress = QProgressDialog("", "Abort", 0, 50000, self)
    progress.setWindowTitle("Searching...")
    progress.setWindowModality(Qt.Qt.WindowModal)
    progress.setValue(0)
    progress.setMinimumDuration(0)
    
    width = self.width()
    height = self.height()
    x = self.x()
    y = self.y()
    
    self.re_flags = re.UNICODE | re.MULTILINE
    
    if not self.ui.chkAdvRegex.isChecked():
      query = re.escape(query)
    
    if not self.ui.chkAdvCase.isChecked():
      self.re_flags |= re.IGNORECASE
    
    if self.ui.chkAdvNewline.isChecked():
      self.re_flags |= re.DOTALL
    
    self.query_re = re.compile(query, self.re_flags)
    
    dir_filter  = common.qt_to_unicode(self.ui.txtFilterRe.text())
    if dir_filter == "":
      filter_re = script_analytics.DEFAULT_FILTER
    else:
      filter_re = re.compile(dir_filter, re.IGNORECASE | re.DOTALL | re.UNICODE)
    
    self.search_flags = 0
    if self.ui.chkAdvTrans.isChecked():
      self.search_flags |= script_analytics.SEARCH_TRANSLATED
    if self.ui.chkAdvOrig.isChecked():
      self.search_flags |= script_analytics.SEARCH_ORIGINAL
    if self.ui.chkAdvComments.isChecked():
      self.search_flags |= script_analytics.SEARCH_COMMENTS
    
    if self.ui.chkAdvNoTags.isChecked():
      self.search_flags |= script_analytics.SEARCH_NOTAGS
    
    matches = []
    for i, total, filename, partial_results in script_analytics.SA.search_gen(self.query_re, filter_re, self.search_flags):
      
      if progress.wasCanceled():
        break
      
      progress.setValue(i)
      progress.setMaximum(total)
      progress.setLabelText(filename)
      
      # Re-center the dialog.
      progress_w = progress.geometry().width()
      progress_h = progress.geometry().height()
      
      new_x = x + ((width - progress_w) / 2)
      new_y = y + ((height - progress_h) / 2)
      
      progress.move(new_x, new_y)
      
      matches.extend(partial_results)
    
    progress.close()
    
    return matches
  
  ##############################################################################
  ### @fn   changedSearchFilter()
  ### @desc Triggered when the user clicks one of the search filter checkboxes.
  ##############################################################################
  def changedSearchFilter(self):
    PROLOGUE_RE = ur"e00"
    CH1_RE      = ur"e01"
    CH2_RE      = ur"e02|ldive_s01"
    CH3_RE      = ur"e03"
    CH4_RE      = ur"e04"
    CH5_RE      = ur"e05"
    CH6_RE      = ur"e06"
    EPILOGUE_RE = ur"e07"
    FREETIME_RE = ur"e08_00[1-9]|e08_01[0-5]"
    ISLAND_RE   = ur"e09"
    NOVEL_RE    = ur"novel"
    SYS_RE      = ur"jp\\script\\\d\d|MAP_\d\d\d"
    MISC_RE     = ur"e08_100|e08_150|e08_151|e08_152|event|voice"
    
    # If everything's checked, just leave the regex line blank
    # since blank means we'll search everything.
    all_checked = True
    
    for i in range(self.ui.layoutSearchFilter.count()):
      item = self.ui.layoutSearchFilter.itemAt(i)
      if item and not item.widget().isChecked():
        all_checked = False
        break
    
    if all_checked:
      self.ui.txtFilterRe.clear()
      return
    
    # Otherwise, grab each of the individual checkbox statuses
    # and generate a regex from that.
    active_re   = []
    
    if self.ui.chkSearchPlg.isChecked():
      active_re.append(PROLOGUE_RE)
      
    if self.ui.chkSearchCh1.isChecked():
      active_re.append(CH1_RE)
      
    if self.ui.chkSearchCh2.isChecked():
      active_re.append(CH2_RE)
      
    if self.ui.chkSearchCh3.isChecked():
      active_re.append(CH3_RE)
      
    if self.ui.chkSearchCh4.isChecked():
      active_re.append(CH4_RE)
      
    if self.ui.chkSearchCh5.isChecked():
      active_re.append(CH5_RE)
      
    if self.ui.chkSearchCh6.isChecked():
      active_re.append(CH6_RE)
    
    if self.ui.chkSearchEpg.isChecked():
      active_re.append(EPILOGUE_RE)
    
    if self.ui.chkSearchFt.isChecked():
      active_re.append(FREETIME_RE)
    
    if self.ui.chkSearchIsl.isChecked():
      active_re.append(ISLAND_RE)
    
    if self.ui.chkSearchNvl.isChecked():
      active_re.append(NOVEL_RE)
    
    if self.ui.chkSearchSys.isChecked():
      active_re.append(SYS_RE)
    
    if self.ui.chkSearchEtc.isChecked():
      active_re.append(MISC_RE)
    
    self.ui.txtFilterRe.setText("|".join(active_re))
  
  ##############################################################################
  ### @fn   filterSetAll(checked)
  ### @desc Triggered when the user clicks one of the select all/none buttons.
  ##############################################################################
  def filterSetAll(self, checked):
    if checked:
      state = Qt.Qt.Checked
    else:
      state = Qt.Qt.Unchecked
    
    for i in range(self.ui.layoutSearchFilter.count()):
      item = self.ui.layoutSearchFilter.itemAt(i)
      if item:
        item.widget().setCheckState(state)
  
  ##############################################################################
  ### @fn   doubleClicked()
  ### @desc Triggered when the user double-clicks on an item in the tree.
  ##############################################################################
  def doubleClicked(self, item, column):
    if item.childCount() == 0:
      self.changedSelection(item, None)
      self.accept()
  
  ##############################################################################
  ### @fn   changedSelection()
  ### @desc Triggered when the user selects something in the tree.
  ##############################################################################
  def changedSelection(self, current, prev):
    if current == None or current.childCount() != 0:
      return
    
    file = common.qt_to_unicode(current.text(0))
    path = tree.tree_item_to_path(current.parent())
    path = dir_tools.expand_dir(path)
    
    filename = os.path.join(common.editor_config.data01_dir, path, file)
    
    if not os.path.isfile(filename):
      self.ui.txtTranslated.setPlainText("Could not load \"%s\"." % file)
      self.ui.txtOriginal.setPlainText("")
      self.ui.txtComments.setPlainText("")
      return
    
    script_file = ScriptFile(filename)
    
    notags = self.search_flags & script_analytics.SEARCH_NOTAGS
    
    self.ui.txtTranslated.setPlainText(script_file.notags[common.editor_config.lang_trans] if notags else script_file[common.editor_config.lang_trans])
    self.ui.txtOriginal.setPlainText(script_file.notags[common.editor_config.lang_orig] if notags else script_file[common.editor_config.lang_orig])
    self.ui.txtComments.setPlainText(script_file.comments)
    
    self.update_highlights()
  
  ##############################################################################
  ### @fn   update_highlights()
  ### @desc Updates the highlighted text in the 
  ###       For use when the user presses Ctrl+F or in similar situations.
  ##############################################################################
  def update_highlights(self):
    boxes = [self.ui.txtTranslated, self.ui.txtOriginal, self.ui.txtComments]
    
    for box in boxes:
      selections = []
      text = common.qt_to_unicode(box.toPlainText())
      cursor = QTextCursor(box.document())
      
      base_sel = QTextEdit.ExtraSelection()
      base_sel.cursor = cursor
      base_sel.format.setForeground(QColor(255, 0, 0))
      
      for match in self.query_re.finditer(text):
        sel = QTextEdit.ExtraSelection(base_sel)
        sel.cursor.setPosition(match.start(), QTextCursor.MoveAnchor)
        sel.cursor.setPosition(match.end(), QTextCursor.KeepAnchor)
        selections.append(sel)
      
      box.setExtraSelections(selections)
  
  ##############################################################################
  ### @fn   select_query()
  ### @desc Selects the query and gives the box focus.
  ###       For use when the user presses Ctrl+F or in similar situations.
  ##############################################################################
  def select_query(self):
    self.ui.txtQuery.setFocus(Qt.Qt.OtherFocusReason)
    self.ui.txtQuery.lineEdit().selectAll()
  
  ##############################################################################
  ### @fn   accept()
  ### @desc Overrides the OK button to make sure a folder is selected.
  ##############################################################################
  def accept(self):
    if self.ui.treeResults.currentItem() == None or self.ui.treeResults.currentItem().childCount() != 0:
      return
    self.open_clicked.emit()
  
  ##############################################################################
  ### @fn   show()
  ### @desc Overrides the show routine to place the cursor in the search box.
  ##############################################################################
  def show(self):
    self.select_query()
    super(SearchMenu, self).show()

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = SearchMenu()
  form.show()
  sys.exit(app.exec_())

### EOF ###