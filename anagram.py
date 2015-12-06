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
from ui.anagram import Ui_Anagram

from enum import Enum
import os.path
import re

import common
from anagram_file import AnagramFile
from text_printer import draw_anagram

CHK_TYPE = Enum("Orig", "Trans")
CHK_DIFF = Enum("Easy", "Norm", "Hard")
CHK_VAL  = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

################################################################################
### @fn   to_fullwidth(text)
### @desc Convert text to a fullwidth.
################################################################################
def to_fullwidth(text):
  return re.sub(u"[\u0021-\u007e]", lambda x: unichr(ord(x.group(0)) + 0xfee0), text)
  
################################################################################
### @fn   sanitize_text(text)
### @desc Convert text to a format useful for the anagram mode.
################################################################################
def sanitize_text(text):
  text = common.qt_to_unicode(text)
  text = text.upper()
  text = to_fullwidth(text)
  text = re.sub("\s", "", text)
  
  return text

class AnagramEditor(QtGui.QDialog):
  def __init__(self, parent = None):
    super(AnagramEditor, self).__init__(parent)
    
    self.ui = Ui_Anagram()
    self.ui.setupUi(self)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.anagram = None
    
    # Better than doing it manually in Qt Designer.
    for diff in CHK_DIFF:
      for i in range(15):
        self.connect(self.get_check(CHK_TYPE.Trans, diff, i + 1), QtCore.SIGNAL("clicked(bool)"), self.check_clicked)
    
    # They don't need to be editable.
    for diff in CHK_DIFF:
      for i in range(15):
        self.get_check(CHK_TYPE.Orig, diff, i + 1).setEnabled(False)
    
    self.update_checks()
  
  ##############################################################################
  ### @fn   load()
  ### @desc Load an anagram dat file.
  ##############################################################################
  def load(self, filename):
    if not os.path.isfile(filename):
      QtGui.QMessageBox.critical(self, "File Not Found", "Couldn't find \"" + filename + "\"")
      self.reject()
      return
    
    self.anagram = AnagramFile(filename)
    
    self.setWindowTitle("Anagram Editor - " + os.path.basename(filename))
    
    self.ui.txtSolutionTrans.setText(self.anagram.solution[common.editor_config.lang_trans])
    self.ui.txtSolutionOrig.setText(self.anagram.solution[common.editor_config.lang_orig])
    self.ui.txtExtraTrans.setText(self.anagram.extra[common.editor_config.lang_trans])
    self.ui.txtExtraOrig.setText(self.anagram.extra[common.editor_config.lang_orig])
    
    self.set_checks(CHK_TYPE.Trans, CHK_DIFF.Easy, self.anagram.easy)
    self.set_checks(CHK_TYPE.Trans, CHK_DIFF.Norm, self.anagram.normal)
    self.set_checks(CHK_TYPE.Trans, CHK_DIFF.Hard, self.anagram.hard)
    
    self.set_checks(CHK_TYPE.Orig, CHK_DIFF.Easy, self.anagram.easy_orig)
    self.set_checks(CHK_TYPE.Orig, CHK_DIFF.Norm, self.anagram.normal_orig)
    self.set_checks(CHK_TYPE.Orig, CHK_DIFF.Hard, self.anagram.hard_orig)
    
    # The translation side is updated automatically because the text box changes.
    self.update_checks(CHK_TYPE.Orig)
    self.update_preview()
    
  ##############################################################################
  ### @fn   save()
  ### @desc Save the anagram dat file, with backups/changes.
  ##############################################################################
  def save(self):
    
    source   = self.anagram.filename
    filename = os.path.basename(self.anagram.filename)
    
    # First, make the backup.
    self.anagram.backup()
    
    # Then save a copy of our changes for easy access.
    change_file = os.path.join(common.editor_config.changes_dir, filename)
    self.anagram.save(change_file)
    
    # Then save for real.
    self.anagram.save()
  
  ##############################################################################
  ### @fn   get_check()
  ### @desc Returns the checkbox object for a type, difficulty, and value.
  ##############################################################################
  def get_check(self, type, difficulty, value):
    if not type == CHK_TYPE.Orig and not type == CHK_TYPE.Trans:
      return None
    
    if not difficulty == CHK_DIFF.Easy and not difficulty == CHK_DIFF.Norm and not difficulty == CHK_DIFF.Hard:
      return None
    
    if not value in CHK_VAL:
      return None
    
    return vars(self.ui)["chk%s%s%d" % (str(type), str(difficulty), value)]
  
  ##############################################################################
  ### @fn   update_preview()
  ### @desc Updates the preview image.
  ##############################################################################
  def update_preview(self):
    
    image = draw_anagram(self.anagram)
    pixmap = QtGui.QPixmap.fromImage(image)
    self.ui.lblPreview.setPixmap(pixmap)
  
  ##############################################################################
  ### @fn   check_clicked()
  ### @desc What happens when a check is clicked.
  ##############################################################################
  def check_clicked(self):
    
    self.store_checks()
    self.update_preview()
  
  ##############################################################################
  ### @fn   store_checks()
  ### @desc Take the check boxes and store their values in our anagram.
  ##############################################################################
  def store_checks(self):
    
    if not self.anagram == None:
      self.anagram.easy = self.checks_to_list(CHK_TYPE.Trans, CHK_DIFF.Easy)
      self.anagram.normal = self.checks_to_list(CHK_TYPE.Trans, CHK_DIFF.Norm)
      self.anagram.hard = self.checks_to_list(CHK_TYPE.Trans, CHK_DIFF.Hard)
  
  ##############################################################################
  ### @fn   set_checks()
  ### @desc Checks/unchecks the checkboxes based on a list of shown letters.
  ##############################################################################
  def set_checks(self, type, difficulty, shown):
    
    for i in range(1, 16):
      checked = False
      if not shown == None and i in shown:
        checked = True
      
      self.get_check(type, difficulty, i).setChecked(checked)
  
  ##############################################################################
  ### @fn   checks_to_list(type, difficulty)
  ### @desc Converts the check boxes into a list of shown letters.
  ##############################################################################
  def checks_to_list(self, type, difficulty):
    text = ""
    
    if type == CHK_TYPE.Trans:
      text = common.qt_to_unicode(self.ui.txtSolutionTrans.text())
    else:
      text = common.qt_to_unicode(self.ui.txtSolutionOrig.text())
    
    letters = len(text)
    
    shown = []
    
    for i in range(1, letters + 1):
      if self.get_check(type, difficulty, i).isChecked():
        shown.append(i)
    
    return shown
  
  ##############################################################################
  ### @fn   update_checks(type)
  ### @desc Enables/disables check boxes as necessary.
  ##############################################################################
  def update_checks(self, type = CHK_TYPE.Trans):
    text = ""
    
    if type == CHK_TYPE.Trans:
      text = common.qt_to_unicode(self.ui.txtSolutionTrans.text())
    else:
      text = common.qt_to_unicode(self.ui.txtSolutionOrig.text())
    
    letters = len(text)
    
    for diff in CHK_DIFF:
      for i in range(1, letters + 1):
        # Only enable the check boxes for translation mode, since they can't
        # edit the originals.
        if type == CHK_TYPE.Trans:
          self.get_check(type, diff, i).setEnabled(True)
        self.get_check(type, diff, i).setVisible(True)
      for i in range(letters + 1, 16):
        self.get_check(type, diff, i).setEnabled(False)
        self.get_check(type, diff, i).setChecked(False)
        self.get_check(type, diff, i).setVisible(False)
  
  ##############################################################################
  ### @fn   changedSolution(text)
  ### @desc Triggered when the solution box is changed, either manually or
  ###       programatically.
  ##############################################################################
  def changed_solution(self, text):
    self.update_checks(CHK_TYPE.Trans)
    self.update_preview()
  
  ##############################################################################
  ### @fn   editedSolution(text)
  ### @desc Triggered when the solution box is edited manually--
  ###       NOT programatically.
  ##############################################################################
  def edited_solution(self, text):
    text = sanitize_text(text)
    
    cursor = self.ui.txtSolutionTrans.cursorPosition()
    self.ui.txtSolutionTrans.setText(text)
    self.ui.txtSolutionTrans.setCursorPosition(cursor)
    
    self.anagram.solution[common.editor_config.lang_trans] = text
    
    self.store_checks()
  
  ##############################################################################
  ### @fn   editedExtra(text)
  ### @desc Triggered when the extra box is edited manually--
  ###       NOT programatically.
  ##############################################################################
  def edited_extra(self, text):
    text = sanitize_text(text)
    
    cursor = self.ui.txtExtraTrans.cursorPosition()
    self.ui.txtExtraTrans.setText(text)
    self.ui.txtExtraTrans.setCursorPosition(cursor)
    
    self.anagram.extra[common.editor_config.lang_trans] = text
  
  ##############################################################################
  ### @fn   accept()
  ### @desc Overrides the Save button.
  ##############################################################################
  def accept(self):
    if self.anagram.solution[common.editor_config.lang_trans] == "" or self.anagram.extra[common.editor_config.lang_trans] == "":
      QtGui.QMessageBox.critical(self, "No Translation", "Please fill in the translation boxes.")
      return
    
    self.save()
    
    super(AnagramEditor, self).accept()
  
  ##############################################################################
  ### @fn   reject()
  ### @desc Overrides the Cancel button.
  ##############################################################################
  def reject(self):
    super(AnagramEditor, self).reject()

#if __name__ == '__main__':
  #import sys

  #app = QtGui.QApplication(sys.argv)
  #app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              #app,
              #QtCore.SLOT("quit()")
             #)
  
  #form = AnagramEditor()
  #form.load("umdimage/anagram_11.dat")
  #form.show()
  #sys.exit(app.exec_())

### EOF ###