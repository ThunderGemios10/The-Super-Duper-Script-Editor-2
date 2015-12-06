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

################################################################################
### This is probably the worst code I have ever written.
### 
### It does a bunch of stupid shit for the sake of storing the list of terms
### on a networked location (i.e. our Dropbox folder).
################################################################################

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtCore import QString
from ui.terminology import Ui_TerminologyEditor

from enum import Enum
import os.path
import re

import common
from term_edit import TermEdit
from terminology import *

class TerminologyEditor(QtGui.QDialog):
  def __init__(self, parent = None):
    super(TerminologyEditor, self).__init__(parent)
    
    self.ui = Ui_TerminologyEditor()
    self.ui.setupUi(self)
    #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.build_ui()
  
  def show(self):
    self.refresh_ui()
    super(TerminologyEditor, self).show()
  
  ##############################################################################
  ### @fn   add_term_button()
  ### @desc Triggered by a button-press.
  ##############################################################################
  def add_term_button(self):
    word, meaning = self.show_term_editor()
    
    if word == None or meaning == None:
      return
    
    new_term = Term(common.qt_to_unicode(word), common.qt_to_unicode(meaning))
    section = common.qt_to_unicode(self.get_section())
    
    if term_exists(section, new_term):
      QtGui.QMessageBox.warning(
        self,
        "Term Exists",
        "The term you are trying to add already exists.",
        buttons = QtGui.QMessageBox.Ok,
        defaultButton = QtGui.QMessageBox.Ok
      )
      return
    
    add_term(section, new_term)
    self.refresh_ui()
  
  ##############################################################################
  ### @fn   edit_term()
  ### @desc Triggered by a button-press.
  ##############################################################################
  def edit_term(self):
    old_word, old_meaning = self.get_current_term()
    word, meaning = self.show_term_editor(old_word, old_meaning)
    
    if word == None or meaning == None:
      return
    
    if word == old_word and meaning == old_meaning:
      return
    
    old_term = Term(common.qt_to_unicode(old_word), common.qt_to_unicode(old_meaning))
    new_term = Term(common.qt_to_unicode(word),     common.qt_to_unicode(meaning))
    section = common.qt_to_unicode(self.get_section())
    
    if term_exists(section, new_term):
      QtGui.QMessageBox.warning(
        self,
        "Term Exists",
        "The term you are trying to add already exists.",
        buttons = QtGui.QMessageBox.Ok,
        defaultButton = QtGui.QMessageBox.Ok
      )
      return
    
    replace_term(section, old_term, new_term)
    self.refresh_ui()
  
  ##############################################################################
  ### @fn   delete_term()
  ### @desc Triggered by a button-press.
  ##############################################################################
  def delete_term(self):
  
    answer = QtGui.QMessageBox.question(
      self,
      "Delete Term",
      "Are you sure you want to delete the currently selected term?",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    section = common.qt_to_unicode(self.get_section())
    word, meaning = self.get_current_term()
    
    term = Term(common.qt_to_unicode(word), common.qt_to_unicode(meaning))
    remove_term(section, term)
    
    self.refresh_ui()
  
  ##############################################################################
  ### @fn   show_term_editor(word, meaning)
  ### @desc Shows an editor window for a term. Word/meaning are default values.
  ##############################################################################
  def show_term_editor(self, word = "", meaning = ""):
    editor = TermEdit()
    editor.ui.txtJapanese.setText(word)
    editor.ui.txtEnglish.setText(meaning)
    if editor.exec_() == QtGui.QDialog.Accepted:
      word = editor.ui.txtJapanese.text()
      meaning = editor.ui.txtEnglish.text()
    else:
      word = None
      meaning = None
    
    return word, meaning
  
  ##############################################################################
  ### @fn   add_section_button()
  ### @desc Triggered by a button-press.
  ##############################################################################
  def add_section_button(self):
    
    section = self.show_section_editor()
    
    if section == None:
      return
    
    if section_exists(common.qt_to_unicode(section)):
      QtGui.QMessageBox.warning(
        self,
        "Section Exists",
        "The section \"" + section + "\" already exists.",
        buttons = QtGui.QMessageBox.Ok,
        defaultButton = QtGui.QMessageBox.Ok
      )
      self.show_section(section)
      return
    
    add_term(common.qt_to_unicode(section), Term(u"プレイスホルダー", u"Placeholder"))
    self.refresh_ui()
    self.show_section(section)
  
  ##############################################################################
  ### @fn   rename_section()
  ### @desc Triggered by a button-press.
  ##############################################################################
  def rename_section(self):
    old_section = self.get_section()
    new_section = self.show_section_editor(old_section)
    
    if new_section == None:
      return
    
    if old_section == new_section:
      return
    
    # All this encoding conversion shit is confusing me.
    if section_exists(common.qt_to_unicode(new_section)):
      answer = QtGui.QMessageBox.warning(
        self,
        "Section Exists",
        "The section \"" + new_section + "\" already exists.\n\n" + 
        "By renaming \"" + old_section + "\" to \"" + new_section + "\", the two sections will be merged.\n\n" +
        "Proceed?",
        buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        defaultButton = QtGui.QMessageBox.Cancel
      )
      
      if answer == QtGui.QMessageBox.Cancel:
        return
    
    rename_section(common.qt_to_unicode(old_section), common.qt_to_unicode(new_section))
    self.refresh_ui()
    self.show_section(new_section)
    
  ##############################################################################
  ### @fn   delete_section()
  ### @desc Triggered by a button-press.
  ##############################################################################
  def delete_section(self):
    section = self.get_section()
    
    answer = QtGui.QMessageBox.question(
      self,
      "Delete Section",
      "Are you sure you want to delete the section \"" + section + "\"?",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    remove_section(common.qt_to_unicode(section))
    self.refresh_ui()
  
  ##############################################################################
  ### @fn   show_section_editor(word, meaning)
  ### @desc Shows an editor window for a section name. section = default
  ##############################################################################
  def show_section_editor(self, section = ""):
    dialog = QtGui.QInputDialog(self)
    dialog.setInputMode(QtGui.QInputDialog.TextInput)
    dialog.setLabelText("Enter the section name.")
    dialog.setWindowTitle("Section")
    dialog.setTextValue(section)
    
    if dialog.exec_() == QtGui.QDialog.Accepted:
      section = dialog.textValue()
    else:
      section = None
    
    return section
  
  ##############################################################################
  ### @fn   find_section()
  ### @desc Returns the tab index of the section given.
  ##############################################################################
  def find_section(self, section):
    
    for i in range(self.ui.tabTerminology.count()):
      this_section = self.ui.tabTerminology.tabText(i)
      
      if this_section.toLower() == section.toLower():
        return i
    
    return -1
  
  ##############################################################################
  ### @fn   show_section()
  ### @desc Shows the tab for the given section.
  ##############################################################################
  def show_section(self, section):
    
    index = self.find_section(section)
    
    if not index == -1:
      self.ui.tabTerminology.setCurrentIndex(index)
  
  ##############################################################################
  ### @fn   get_row()
  ### @desc Returns the currently selected row in the current tab.
  ##############################################################################
  def get_row(self):
    
    current_tree = self.ui.tabTerminology.currentWidget()
    rows = current_tree.selectionModel().selectedRows()
    
    # Only one selectable anyway, so we're good here.
    if len(rows) >= 1:
      return rows[0].row()
  
  ##############################################################################
  ### @fn   get_term()
  ### @desc Returns the word/meaning pair for the given row.
  ##############################################################################
  def get_term(self, row):
    
    current_tree = self.ui.tabTerminology.currentWidget()
    item = current_tree.topLevelItem(row)
    
    word =    item.text(0)
    meaning = item.text(1)
    
    return word, meaning
  
  ##############################################################################
  ### @fn   get_current_term()
  ### @desc Returns the word/meaning pair for the currently selected row.
  ##############################################################################
  def get_current_term(self):
    return self.get_term(self.get_row())
  
  ##############################################################################
  ### @fn   get_section()
  ### @desc Returns the section header for the currently visible tab.
  ##############################################################################
  def get_section(self):
    
    current_tab = self.ui.tabTerminology.currentIndex()
    section = self.ui.tabTerminology.tabText(current_tab)
    
    return section
  
  ##############################################################################
  ### @fn   refresh_ui()
  ### @desc Rebuilds the UI.
  ##############################################################################
  def refresh_ui(self):
    current_tab = self.ui.tabTerminology.currentIndex()
    self.build_ui()
    self.ui.tabTerminology.setCurrentIndex(current_tab)
  
  ##############################################################################
  ### @fn   build_ui()
  ### @desc Creates a UI from the terminology CSV file.
  ##############################################################################
  def build_ui(self):
    terminology = load_csv()
    terminology_dict = {}
    
    for item in terminology:
      section = QString(item['Section'].decode("UTF-8"))
      
      if not section in terminology_dict:
        terminology_dict[section] = []
      
      terminology_dict[section].append(Term(item['Word'].decode("UTF-8"), item['Meaning'].decode("UTF-8")))
    
    sections = sorted(terminology_dict.keys())
    
    self.ui.tabTerminology.clear()
    
    for section in sections:
      self.__ui_add_section(section)
      
      for word in terminology_dict[section]:
        self.__ui_add_term(word)
      
      self.ui.tabTerminology.currentWidget().setCurrentItem(self.ui.tabTerminology.currentWidget().topLevelItem(0))
    
    self.ui.tabTerminology.setCurrentIndex(0)
    
  ##############################################################################
  ### @fn   ui_add_section()
  ### @desc Adds a new tab to the UI. Used by build_ui.
  ##############################################################################
  def __ui_add_section(self, section):
    
    tree_widget = QtGui.QTreeWidget()
    tree_widget.header().setDefaultSectionSize(180)
    tree_widget.setGeometry(QtCore.QRect(-1, 0, 360, 301))
    tree_widget.setFrameShape(QtGui.QFrame.NoFrame)
    tree_widget.setRootIsDecorated(False)
    tree_widget.setColumnCount(2)
    tree_widget.setHeaderLabels(["Original", "Translated"])
    tree_widget.setSortingEnabled(True)
    tree_widget.sortItems(0, Qt.Qt.AscendingOrder)
    self.ui.tabTerminology.addTab(tree_widget, section)
    
    self.show_section(section)
  
  ##############################################################################
  ### @fn   ui_add_term()
  ### @desc Creates a UI from the terminology CSV file.
  ##############################################################################
  def __ui_add_term(self, term):
    
    current_tree = self.ui.tabTerminology.currentWidget()
    new_term = QtGui.QTreeWidgetItem([term.word, term.meaning])
    current_tree.addTopLevelItem(new_term)
    current_tree.setCurrentItem(new_term)

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = TerminologyEditor()
  form.show()
  sys.exit(app.exec_())

### EOF ###