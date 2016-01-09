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

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QTextCursor
from ui.eboot import Ui_EbootEditor

import common

class EbootEditor(QtGui.QDialog):
  def __init__(self, parent=None):
    super(EbootEditor, self).__init__(parent)
    
    self.ui = Ui_EbootEditor()
    self.ui.setupUi(self)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.ui.actionNextLine = QtGui.QAction("Next line", None, triggered = self.nextLine)
    self.ui.actionPrevLine = QtGui.QAction("Previous line", None, triggered = self.prevLine)
    
    self.ui.actionNextLine.setShortcut("PgDown")
    self.ui.actionPrevLine.setShortcut("PgUp")
    
    self.addAction(self.ui.actionNextLine)
    self.addAction(self.ui.actionPrevLine)
    
    self.lines = eboot_text.get_eboot_text()
    
    self.current_line = 0
    
    self.max_len = 0
    
    for line in self.lines:
      self.ui.lstLines.addItem("Pos: " + line.pos.hex)
    
    self.ui.lstLines.setCurrentRow(0)
  
  ##############################################################################
  ### @fn   updateSpellCheck()
  ### @desc Updates the spellchecker based on our setting.
  ##############################################################################
  def updateSpellCheck(self):
    if common.editor_config.spell_check != self.ui.txtTranslated.spellcheck_enabled():
      if common.editor_config.spell_check:
        self.ui.txtTranslated.enable_spellcheck()
      else:
        self.ui.txtTranslated.disable_spellcheck()
    
    if common.editor_config.spell_check_lang != self.ui.txtTranslated.get_language():
      self.ui.txtTranslated.set_language(common.editor_config.spell_check_lang)
  
  ##############################################################################
  ### @fn   changedTranslation()
  ### @desc asd
  ##############################################################################
  def changedTranslation(self):
    text = common.qt_to_unicode(self.ui.txtTranslated.toPlainText())
    
    bytes  = bytearray(text, encoding = self.lines[self.current_line].enc)
    length = len(bytes)
    
    self.ui.lblTransLength.setText("Length: %d bytes" % length)
    
    if not text == self.lines[self.current_line].text:
      
      if length > self.max_len:
        cursor = self.ui.txtTranslated.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.deletePreviousChar()
        self.ui.txtTranslated.setTextCursor(cursor)
      
      else:
        self.lines[self.current_line].text = text
  
  ##############################################################################
  ### @fn   changedLine()
  ### @desc asd
  ##############################################################################
  def changedLine(self, index):
    self.updateSpellCheck()
    
    self.current_line = index
    
    self.ui.txtTranslated.setPlainText(self.lines[index].text)
    self.ui.txtOriginal.setPlainText(self.lines[index].orig)
    self.ui.txtEncoding.setText(self.lines[index].enc)
    
    bytes = bytearray(self.lines[index].orig, encoding = self.lines[index].enc)
    
    self.ui.lblOrigLength.setText("Length: %d bytes" % len(bytes))
    
    self.max_len = len(bytes)
    
  ##############################################################################
  ### @fn   nextLine()
  ### @desc Selects the next line in the list. Triggered by PgDn.
  ##############################################################################
  def nextLine(self):
    current_row = self.ui.lstLines.currentRow()
    if current_row < self.ui.lstLines.count() - 1:
      self.ui.lstLines.setCurrentRow(current_row + 1)
  
  ##############################################################################
  ### @fn   prevLine()
  ### @desc Selects the previous line in the list. Triggered by PgUp.
  ##############################################################################
  def prevLine(self):
    current_row = self.ui.lstLines.currentRow()
    if current_row > 0:
      self.ui.lstLines.setCurrentRow(current_row - 1)
  
  ##############################################################################
  ### @fn   accept()
  ### @desc Overrides the Save button.
  ##############################################################################
  def accept(self):
    answer = QtGui.QMessageBox.question(
      self,
      "Save Changes",
      "Would you like to save your changes?",
      buttons = QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel,
      defaultButton = QtGui.QMessageBox.Cancel
    )
    
    if answer == QtGui.QMessageBox.Cancel:
      return
      
    elif answer == QtGui.QMessageBox.Discard:
      super(EbootEditor, self).reject()
      return
      
    elif answer == QtGui.QMessageBox.Save:
      eboot_text.text_to_csv(self.lines)
      super(EbootEditor, self).accept()
      return
  
  ##############################################################################
  ### @fn   reject()
  ### @desc Overrides the Cancel button.
  ##############################################################################
  def reject(self):
    super(EbootEditor, self).reject()

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = EbootEditor()
  form.show()
  sys.exit(app.exec_())

### EOF ###
