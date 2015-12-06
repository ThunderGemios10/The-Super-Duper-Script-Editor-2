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
from ui.progresscalculator import Ui_ProgressCalculator

import itertools
import os
import re
import time

import common
import dupe_db
import list_files
import script_file
import script_analytics
from script_file import ScriptFile
from word_count import count_words

UPDATE_INTERVAL = 25

class ProgressCalculator(QtGui.QDialog):
  def __init__(self, parent = None, start_dir = ""):
    super(ProgressCalculator, self).__init__(parent)
    
    self.ui = Ui_ProgressCalculator()
    self.ui.setupUi(self)
    
    # Because I don't feel like doing this in Designer.
    for i in range(self.ui.layoutSearchFilter.count()):
      item = self.ui.layoutSearchFilter.itemAt(i).widget()
      item.stateChanged.connect(self.changedSearchFilter)
    
    self.ui.btnFilterSelAll.clicked.connect(lambda: self.filterSetAll(True))
    self.ui.btnFilterSelNone.clicked.connect(lambda: self.filterSetAll(False))
    
    self._canceled = False
    self._running  = False
  
  def _cancel(self):
    self._canceled = True
  
  def calculate_progress(self):
    dir_filter = common.qt_to_unicode(self.ui.txtFilterRe.text())
    if dir_filter == "":
      dir_filter_re = script_analytics.DEFAULT_FILTER
    else:
      dir_filter_re = re.compile(dir_filter, re.IGNORECASE | re.DOTALL | re.UNICODE)
    
    self._calculate_progress(dir_filter_re)

  # def calculate_progress(self, dir_filter = script_analytics.DEFAULT_FILTER):
  def _calculate_progress(self, dir_filter = script_analytics.DEFAULT_FILTER):
    if self._running:
      return
    
    self._running  = True
    self._canceled = False
    
    self.ui.lblResults.setText("<center><b>Results</b></center>")
    
    start_time = time.time()
    
    self.ui.progressBar.setMaximum(72000)
    self.ui.progressBar.setValue(0)
    
    # For our dupe database, we need the relative location of our files, not absolute.
    dir_start = len(common.editor_config.data01_dir) + 1
    
    total_files = 0
    unique_files = 0
    translated_files = 0
    translated_unique = 0
    
    total_chars = 0
    unique_chars = 0
    translated_chars = 0
    translated_unique_chars = 0
    
    translated_words = 0
    translated_unique_words = 0
    
    total_bytes = 0
    unique_bytes = 0
    translated_bytes = 0
    translated_unique_bytes = 0
    
    groups_seen = set()
    files_seen = set()
    
    untranslated_lines = []
    
    next_update = UPDATE_INTERVAL
    
    for i, total, filename, data in script_analytics.SA.get_data(dir_filter):
      if self._canceled:
        self._running  = False
        self._canceled = False
        self.ui.progressBar.setValue(0)
        self.ui.lblTimeElapsed.setText("00:00")
        return
      
      if i >= next_update:
        self.ui.progressBar.setValue(i)
        self.ui.progressBar.setMaximum(total)
        self.ui.lblTimeElapsed.setText("%02d:%02d" % (divmod(time.time() - start_time, 60)))
        QtGui.QApplication.processEvents()
        next_update = i + UPDATE_INTERVAL
      
      if data == None:
        continue
      
      db_name   = filename
      real_name = os.path.join(common.editor_config.data01_dir, filename)
      
      if db_name in files_seen:
        continue
      
      dupe_group = dupe_db.db.group_from_file(db_name)
      
      # Add the whole group to the translated files, but only one
      # to the unique translated. If there is no group, it's size 1.
      group_size = 1
      
      if not dupe_group == None:
        if dupe_group in groups_seen:
          continue
        else:
          groups_seen.add(dupe_group)
          group_files = dupe_db.db.files_in_group(dupe_group)
          group_files = filter(dir_filter.search, group_files)
          group_size  = len(group_files)
          files_seen.update(group_files)
      
      total_files += group_size
      unique_files += 1
      
      #file = script_for_counting(data)
      file = data
      
      # How many characters is the untranslated, non-tagged text?
      num_chars = len(file.notags[common.editor_config.lang_orig])
      #num_bytes = len(bytearray(file.notags[common.editor_config.lang_orig], encoding = "SJIS", errors = "replace"))
      
      total_chars  += num_chars * group_size
      unique_chars += num_chars
      
      #total_bytes  += num_bytes * group_size
      #unique_bytes += num_bytes
      
      if not file.notags[common.editor_config.lang_trans] == "" or num_chars == 0:
        translated_files  += group_size
        translated_unique += 1
        
        translated_chars        += num_chars * group_size
        translated_unique_chars += num_chars
        
        words = count_words(file.notags[common.editor_config.lang_trans])
        translated_words        += words * group_size
        translated_unique_words += words
        
        #translated_bytes        += num_bytes * group_size
        #translated_unique_bytes += num_bytes
      
      #elif file.notags[common.editor_config.lang_trans] == "":
        #untranslated_lines.append(db_name)
    
    # progress.close()
    self.ui.progressBar.setValue(total)
    #print "Took %s seconds." % (time.time() - start_time)
    
    files_percent         = 100.0 if total_files == 0  else float(translated_files) / total_files * 100
    unique_files_percent  = 100.0 if unique_files == 0 else float(translated_unique) / unique_files * 100
    chars_percent         = 100.0 if total_chars == 0  else float(translated_chars) / total_chars * 100
    unique_chars_percent  = 100.0 if unique_chars == 0 else float(translated_unique_chars) / unique_chars * 100
    bytes_percent         = 100.0 if total_bytes == 0  else float(translated_bytes) / total_bytes * 100
    unique_bytes_percent  = 100.0 if unique_bytes == 0 else float(translated_unique_bytes) / unique_bytes * 100
    
    self.ui.lblResults.setText(
      "<center><b>Results</b></center><br/>" +
      ("<b>Files</b>: %d / %d (%0.2f%%)<br/>" % (translated_files, total_files, files_percent)) + 
      ("<b>Unique Files</b>: %d / %d (%0.2f%%)<br/>" % (translated_unique, unique_files, unique_files_percent)) +
      "<br/>" +
      ("<b>Japanese Characters</b>: %d / %d (%0.2f%%)<br/>" % (translated_chars, total_chars, chars_percent)) + 
      ("<b>Unique Characters</b>: %d / %d (%0.2f%%)<br/>" % (translated_unique_chars, unique_chars, unique_chars_percent)) +
      "<br/>" +
      ("<b>English Words</b>: %d<br/>" % (translated_words)) + 
      ("<b>Unique Words</b>: %d<br/>" % (translated_unique_words)) +
      "<br/>" +
      "<b>NOTE</b>: Unique X is lazy for \"X in all unique files.\""
    )
    
    self._running  = False
    self._canceled = False
  
  ##############################################################################
  ### @fn   changedSearchFilter()
  ### @desc Triggered when the user clicks one of the search filter checkboxes.
  ##        Shamelessly copied from 
  ##############################################################################
  def changedSearchFilter(self):
    PROLOGUE_RE = ur"e00"
    CH1_RE      = ur"e01"
    CH2_RE      = ur"e02"
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

  def list_untranslated(self):
    
    files = list_files.list_all_files(common.editor_config.data01_dir)
    #files = list_files.list_all_files("X:\\Danganronpa\\FULL_TEST\\best-normal")
    
    text_files = []
    
    for i, file in enumerate(files):
      if os.path.splitext(file)[1] == ".txt":
        text_files.append(file)
    
    for file in text_files:
      try:
        script_file = ScriptFile(file)
      except:
        print file
        continue
      
      if not script_file[common.editor_config.lang_trans] == "":
        print file
  
  ##############################################################################
  ### @fn   accept()
  ### @desc Overrides the Close.
  ##############################################################################
  def accept(self):
    if self._running:
      self._cancel()
    super(ProgressCalculator, self).accept()
  
  ##############################################################################
  ### @fn   reject()
  ### @desc Overrides the Cancel button.
  ##############################################################################
  def reject(self):
    if self._running:
      self._cancel()
    super(ProgressCalculator, self).reject()

if __name__ == "__main__":
  import sys
  app = QtGui.QApplication(sys.argv)
  
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = ProgressCalculator()
  form.show()
  sys.exit(app.exec_())
  
  # folder_re = ".*"
  
  # if len(sys.argv) > 1:
    # folder_re = sys.argv[1].decode(sys.stdin.encoding)
  
  # calculate_progress(None, re.compile(folder_re))

### EOF ###