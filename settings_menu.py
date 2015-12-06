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
from PyQt4.QtCore import QSignalMapper
from ui.settingsmenu import Ui_SettingsMenu

import os
import enchant

import common
from dialog_fns import get_save_file, get_open_file, get_existing_dir
import eboot_patch

################################################################################
### So I can loop all this shit and only have to edit stuff
### in one place instead of like fifty.
################################################################################
TEXT    = "text"
BTN     = "btn"
CFG     = "cfg"
CHK     = "chk"
DEFAULT = "def"
FN      = "fn"
FILTER  = "filter"

FILE_LOCATIONS = [
  {TEXT: "txtIsoDir",       BTN: "btnIsoDir",       CFG: "iso_dir",       FN: get_existing_dir, FILTER: None},
  {TEXT: "txtIsoFile",      BTN: "btnIsoFile",      CFG: "iso_file",      FN: get_save_file,    FILTER: "PSP ISO Files (*.iso)"},
  {TEXT: "txtData00Dir",    BTN: "btnData00Dir",    CFG: "data00_dir",    FN: get_existing_dir, FILTER: None},
  {TEXT: "txtData01Dir",    BTN: "btnData01Dir",    CFG: "data01_dir",    FN: get_existing_dir, FILTER: None},
  {TEXT: "txtBuildCache",   BTN: "btnBuildCache",   CFG: "build_cache",   FN: get_existing_dir, FILTER: None},
  {TEXT: "txtGFXDir",       BTN: "btnGFXDir",       CFG: "gfx_dir",       FN: get_existing_dir, FILTER: None},
  {TEXT: "txtVoice",        BTN: "btnVoice",        CFG: "voice_dir",     FN: get_existing_dir, FILTER: None},
  {TEXT: "txtTerminology",  BTN: "btnTerminology",  CFG: "terminology",   FN: get_open_file,    FILTER: "Terminology.csv (*.csv)"},
  {TEXT: "txtDupes",        BTN: "btnDupes",        CFG: "dupes_csv",     FN: get_open_file,    FILTER: "dupes.csv (*.csv)"},
  # {TEXT: "txtEbootText",    BTN: "btnEbootText",    CFG: "eboot_text",    FN: get_open_file,    FILTER: "eboot_text.csv (*.csv)"},
  {TEXT: "txtSimilarity",   BTN: "btnSimilarity",   CFG: "similarity_db", FN: get_open_file,    FILTER: "similarity-db.sql (*.sql)"},
  {TEXT: "txtCopy",         BTN: "btnCopy",         CFG: "changes_dir",   FN: get_existing_dir, FILTER: None},
  {TEXT: "txtBackup",       BTN: "btnBackup",       CFG: "backup_dir",    FN: get_existing_dir, FILTER: None},
]

EDITOR_PREFS_CHK = [
  {CHK: "chkPlayVoices",    CFG: "auto_play_voice", DEFAULT: False},
  {CHK: "chkPlayBGM",       CFG: "auto_play_bgm",   DEFAULT: False},
  {CHK: "chkSpellCheck",    CFG: "spell_check",     DEFAULT: True},
  {CHK: "chkTextRepl",      CFG: "text_repl",       DEFAULT: False},
  {CHK: "chkSmartQuotes",   CFG: "smart_quotes",    DEFAULT: False},
  {CHK: "chkQuickClt",      CFG: "quick_clt",       DEFAULT: False},
  {CHK: "chkTagHighlight",  CFG: "highlight_tags",  DEFAULT: False},
  {CHK: "chkTermHighlight", CFG: "highlight_terms", DEFAULT: True},
  {CHK: "chkMangle",        CFG: "mangle_text",     DEFAULT: True},
  {CHK: "chkPackData00",    CFG: "pack_data00",     DEFAULT: False},
  {CHK: "chkPackData01",    CFG: "pack_data01",     DEFAULT: True},
  {CHK: "chkBuildISO",      CFG: "build_iso",       DEFAULT: True},
  {CHK: "chkExpandTrees",   CFG: "auto_expand",     DEFAULT: True},
  {CHK: "chkQuickBuild",    CFG: "quick_build",     DEFAULT: False},
]

EDITOR_PREFS_TXT = [
  {TEXT: "txtLangOrig",     CFG: "lang_orig",       DEFAULT: "ja"},
  {TEXT: "txtLangTrans",    CFG: "lang_trans",      DEFAULT: "en"},
]

################################################################################
### Settings Menu
################################################################################
class SettingsMenu(QtGui.QDialog):
  def __init__(self, parent = None):
    super(SettingsMenu, self).__init__(parent)
    
    self.ui = Ui_SettingsMenu()
    self.ui.setupUi(self)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.ui.buttonBox.clicked.connect(self.button_clicked)
    
    self.setup_prefs()
    self.setup_file_locs()
    self.setup_tags()
    self.setup_repl()
    self.setup_hacks()
  
################################################################################
### TAB: PREFERENCES
################################################################################
  def setup_prefs(self):
    for item in EDITOR_PREFS_CHK:
      self.ui.__dict__[item[CHK]].setChecked(common.editor_config.get_pref(item[CFG], item[DEFAULT]))
    
    for item in EDITOR_PREFS_TXT:
      self.ui.__dict__[item[TEXT]].setText(common.editor_config.get_pref(item[CFG]))
    
    # And our spellcheck language has to be handled manually.
    self.ui.cboSpellCheckLang.clear()
    self.ui.cboSpellCheckLang.addItems(enchant.list_languages())
    
    lang_index = self.ui.cboSpellCheckLang.findText(common.editor_config.spell_check_lang, Qt.Qt.MatchContains)
    self.ui.cboSpellCheckLang.setCurrentIndex(lang_index)
  
  def apply_prefs(self):
    for item in EDITOR_PREFS_TXT:
      if self.ui.__dict__[item[TEXT]].text().length() == 0:
        QtGui.QMessageBox.critical(self, "Error", "Please provide languages codes for both original and translated text.")
        return False
    
    # Then apply our changes.
    for item in EDITOR_PREFS_TXT:
      common.editor_config.set_pref(item[CFG], common.qt_to_unicode(self.ui.__dict__[item[TEXT]].text(), normalize = False))
        
    for item in EDITOR_PREFS_CHK:
      common.editor_config.set_pref(item[CFG], self.ui.__dict__[item[CHK]].isChecked())
    
    common.editor_config.spell_check_lang = self.ui.cboSpellCheckLang.currentText()
    
    return True

################################################################################
### TAB: FILE LOCATIONS
################################################################################
  # A helper function for our signal mapper.
  # Shows a dialog asking for a file or directory to use in the text box
  # associated with the given index.
  def __get_cfg_item(self, index):
    box     = FILE_LOCATIONS[index][TEXT]
    fn      = FILE_LOCATIONS[index][FN]
    filter  = FILE_LOCATIONS[index][FILTER]
    
    if filter:
      item = fn(self, self.ui.__dict__[box].text(), filter)
    else:
      item = fn(self, self.ui.__dict__[box].text())
    
    if not item == "":
      self.ui.__dict__[box].setText(item)
  
  def setup_file_locs(self):
    
    # Because the default margins are ugly as h*ck.
    self.ui.tabLocs.layout().setContentsMargins(0, 0, 0, 0)
    
    # Map our buttons to functions that retrieve the necessary data.
    cfg_mapper = QSignalMapper(self)
    
    for i, item in enumerate(FILE_LOCATIONS):
      self.connect(self.ui.__dict__[item[BTN]], QtCore.SIGNAL("clicked()"), cfg_mapper, QtCore.SLOT("map()"))
      cfg_mapper.setMapping(self.ui.__dict__[item[BTN]], i)
    
    self.connect(cfg_mapper, QtCore.SIGNAL("mapped(int)"), self.__get_cfg_item)
    
    # Load in all our info from the config file.
    for item in FILE_LOCATIONS:
      self.ui.__dict__[item[TEXT]].setText(common.editor_config.get_pref(item[CFG]))
  
  def apply_file_locs(self):
    # Check to make sure none of our boxes are blank.
    for item in FILE_LOCATIONS:
      if self.ui.__dict__[item[TEXT]].text().length() == 0:
        QtGui.QMessageBox.critical(self, "Error", "Please supply locations for all the listed files or folders.")
        return False
    
    # Then apply our changes.
    for item in FILE_LOCATIONS:
      common.editor_config.set_pref(item[CFG], common.qt_to_unicode(self.ui.__dict__[item[TEXT]].text(), normalize = False))
    
    return True
  
################################################################################
### TAB: TAGS
################################################################################
  def setup_tags(self):
    self.ui.treeTags.clear()
    self.ui.treeTags.header().setResizeMode(QtGui.QHeaderView.Stretch)
    self.ui.tabTags.setEnabled(False)
  
  def apply_tags(self):
    return True
  
  def add_tag(self):
    pass
    
  def del_tag(self):
    pass
    
  def move_tag_up(self):
    pass
    
  def move_tag_down(self):
    pass
    
  def move_tag_top(self):
    pass
    
  def move_tag_bottom(self):
    pass
  
################################################################################
### TAB: TEXT REPLACEMENT
################################################################################
  def setup_repl(self):
    self.ui.treeTextRepl.clear()
    self.ui.treeTextRepl.header().setResizeMode(QtGui.QHeaderView.Stretch)
    self.ui.tabRepl.setEnabled(True)
    
    for src, dst in common.editor_config.repl:
      self.add_repl(src, dst)
  
  def apply_repl(self):
    common.editor_config.repl = []
    
    for i in range(self.ui.treeTextRepl.topLevelItemCount()):
      item = self.ui.treeTextRepl.topLevelItem(i)
      src  = common.qt_to_unicode(item.text(0), normalize = False)
      dst  = common.qt_to_unicode(item.text(1), normalize = False)
      
      common.editor_config.repl.append((src, dst))
      
    return True
  
  def add_repl(self, src = u"???", dst = u"???"):
    new_sub = QtGui.QTreeWidgetItem([src, dst])
    new_sub.setFlags(new_sub.flags() | Qt.Qt.ItemIsEditable)
    self.ui.treeTextRepl.addTopLevelItem(new_sub)
  
  def del_repl(self):
    rows = self.ui.treeTextRepl.selectionModel().selectedRows()
    
    for row in rows:
      self.ui.treeTextRepl.takeTopLevelItem(row.row())
  
################################################################################
### TAB: HACKS
################################################################################
  def setup_hacks(self):
    self.ui.btnReloadHacks.clicked.connect(self.load_hacks)
    self.load_hacks()
  
  def load_hacks(self):
    reload(eboot_patch)
    
    self.ui.lstHacks.clear()
    
    for i, hack in enumerate(eboot_patch.EBOOT_PATCHES):
      name   = hack[eboot_patch.NAME]
      cfg_id = hack[eboot_patch.CFG_ID]
      
      if cfg_id and cfg_id in common.editor_config.hacks:
        enabled = common.editor_config.hacks[cfg_id]
      else:
        enabled = hack[eboot_patch.ENABLED]
      
      self.ui.lstHacks.addItem(name)
      self.ui.lstHacks.item(i).setCheckState(Qt.Qt.Checked if enabled else Qt.Qt.Unchecked)
      
      if cfg_id:
        self.ui.lstHacks.item(i).setData(Qt.Qt.UserRole, cfg_id)
        self.ui.lstHacks.item(i).setFlags(self.ui.lstHacks.item(i).flags() | Qt.Qt.ItemIsEnabled)
      else:
        self.ui.lstHacks.item(i).setData(Qt.Qt.UserRole, "")
        self.ui.lstHacks.item(i).setFlags(self.ui.lstHacks.item(i).flags() & ~Qt.Qt.ItemIsEnabled)
    
    self.ui.cboHackLang.clear()
    
    for lang in eboot_patch.LANGUAGES:
      self.ui.cboHackLang.addItem(lang)
    
    if eboot_patch.LANG_CFG_ID in common.editor_config.hacks:
      sys_lang = common.editor_config.hacks[eboot_patch.LANG_CFG_ID]
      self.ui.cboHackLang.setCurrentIndex(sys_lang)
    else:
      self.ui.cboHackLang.setCurrentIndex(0)
  
  def apply_hacks(self):
    for i in range(self.ui.lstHacks.count()):
      cfg_id  = common.qt_to_unicode(self.ui.lstHacks.item(i).data(Qt.Qt.UserRole).toString())
      enabled = self.ui.lstHacks.item(i).checkState() == Qt.Qt.Checked
      
      if cfg_id:
        common.editor_config.hacks[cfg_id] = enabled
    
    common.editor_config.hacks[eboot_patch.LANG_CFG_ID] = self.ui.cboHackLang.currentIndex()
      
    return True
  
################################################################################
### SLOTS
################################################################################
  def button_clicked(self, button):
    if self.ui.buttonBox.buttonRole(button) == QtGui.QDialogButtonBox.ApplyRole:
      self.apply_settings()
    
  def apply_settings(self):
    if self.apply_prefs() and self.apply_file_locs() and self.apply_tags() and \
       self.apply_repl() and self.apply_hacks():
      
      common.editor_config.save_config()
      return True
    else:
      return False
  
  ##############################################################################
  ### @fn   accept()
  ### @desc Overrides the Save button.
  ##############################################################################
  def accept(self):
    if self.apply_settings() == False:
      return
    
    super(SettingsMenu, self).accept()
  
  ##############################################################################
  ### @fn   reject()
  ### @desc Overrides the Cancel button.
  ##############################################################################
  def reject(self):
    super(SettingsMenu, self).reject()

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = SettingsMenu()
  form.show()
  sys.exit(app.exec_())

### EOF ###