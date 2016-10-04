# -*- coding: utf-8 -*-
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
from PyQt4.QtGui import QProgressDialog, QProgressBar, QTextCursor, QImage, QApplication, QShortcut, QKeySequence
from PyQt4.QtCore import QProcess, QString

from ui.editor import Ui_Editor

from anagram import AnagramEditor
from console import Console
from diffs_menu import DiffsMenu
from eboot_editor import EbootEditor
from font_gen_menu import FontGenMenu
from open_menu import OpenMenu
from script_dump_menu import ScriptDumpMenu
from search_menu import SearchMenu
from settings_menu import SettingsMenu
from terminology_editor import TerminologyEditor

import codecs
import logging
import os
import re
import shutil
import time
from enum import Enum

import backup
import common
from dupe_db import db as dupe_db
import dir_tools
from import_export import *
import script_analytics
import text_printer
from text_format import TEXT_FORMATS
import tree

# from audio.bgm_player import BGMPlayer
from pack.packer import CpkPacker
from list_files import list_all_files
from object_labels import get_map_name, get_char_name, get_obj_label, get_bgm_name
from mtb import MTBParser
from nonstop import NonstopParser
from progress import ProgressCalculator
from script_file import ScriptFile, TAG_KILLER
from script_jump import ScriptJump
from script_pack import ScriptPack
from similarity_db import SimilarityDB
from voice import get_voice_file
from voice_player import VoicePlayer
from word_count import count_words

from iso_builder import IsoBuilder

IMAGE_POS = Enum("original", "translated")

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

################################################################################
###                                                                          ###
### EditorForm Class                                                         ###
###                                                                          ###
################################################################################
class EditorForm(QtGui.QMainWindow):
  def __init__(self, parent = None):
  
    ##############################
    ### VARIABLES
    ##############################
    super(EditorForm, self).__init__(parent)
    self.ui = Ui_Editor()
    self.ui.setupUi(self)
    
    self.directory   = ""
    self.script_pack = ScriptPack()
    self.changed     = []
    self.cur_script  = 0
    
    self.similarity_db = SimilarityDB()
    
    # If there are dupes of a file in the same folder, we want to edit them
    # synchronously, so we keep track of those dupes here.
    self.internal_dupes = {}
    
    self.bg = None
    
    self.console = Console()
    self.iso_builder = IsoBuilder(self)
    
    ##############################
    ### CUSTOM ACTIONS
    ##############################
    self.ui.actionSeparator  = QtGui.QAction("", None)
    self.ui.actionSeparator2 = QtGui.QAction("", None)
    self.ui.actionSeparator .setSeparator(True)
    self.ui.actionSeparator2.setSeparator(True)
    
    ### SAVE IMAGE ###
    self.ui.actionSaveImgTrans = QtGui.QAction("Save image...", None, triggered = (lambda: self.saveImage(IMAGE_POS.translated)))
    self.ui.actionSaveImgOrig  = QtGui.QAction("Save image...", None, triggered = (lambda: self.saveImage(IMAGE_POS.original)))
    self.ui.lblTranslated.addAction(self.ui.actionSaveImgTrans)
    self.ui.lblOriginal.addAction(self.ui.actionSaveImgOrig)
    
    ### COPY NODE PATH ###
    self.ui.actionCopyActivePath    = QtGui.QAction("Copy path", None, triggered = self.copyActivePath)
    self.ui.actionCopyDupePath      = QtGui.QAction("Copy path", None, triggered = (lambda: self.copyNodePath(self.ui.treeDupes.currentItem())))
    self.ui.actionCopySimilarPath   = QtGui.QAction("Copy path", None, triggered = (lambda: self.copyNodePath(self.ui.treeSimilar.currentItem())))
    self.ui.actionCopyReferencePath = QtGui.QAction("Copy path", None, triggered = (lambda: self.copyNodePath(self.ui.treeReferences.currentItem())))
    self.ui.lstFiles      .addAction(self.ui.actionCopyActivePath)
    self.ui.treeDupes     .addAction(self.ui.actionCopyDupePath)
    self.ui.treeSimilar   .addAction(self.ui.actionCopySimilarPath)
    self.ui.treeReferences.addAction(self.ui.actionCopyReferencePath)
    
    # Go to script jump
    self.ui.actionGotoScriptJump    = QtGui.QAction("Jump to folder", None, triggered = self.gotoScriptJump)
    self.ui.lstFiles.addAction(self.ui.actionGotoScriptJump)
    
    ### SEPARATOR ###
    self.ui.lstFiles      .addAction(self.ui.actionSeparator)
    self.ui.treeDupes     .addAction(self.ui.actionSeparator)
    self.ui.treeSimilar   .addAction(self.ui.actionSeparator)
    self.ui.treeReferences.addAction(self.ui.actionSeparator)
    
    ### SHOW FILE IN EDITOR ###
    self.ui.actionShowDupeInEditor        = QtGui.QAction("Show in editor", None, triggered = (lambda: self.showNodeInEditor(self.ui.treeDupes.currentItem())))
    self.ui.actionShowSimilarInEditor     = QtGui.QAction("Show in editor", None, triggered = (lambda: self.showNodeInEditor(self.ui.treeSimilar.currentItem())))
    self.ui.actionShowReferenceInEditor   = QtGui.QAction("Show in editor", None, triggered = (lambda: self.showNodeInEditor(self.ui.treeReferences.currentItem())))
    self.ui.treeDupes     .addAction(self.ui.actionShowDupeInEditor)
    self.ui.treeSimilar   .addAction(self.ui.actionShowSimilarInEditor)
    self.ui.treeReferences.addAction(self.ui.actionShowReferenceInEditor)
    
    ### SHOW FILE IN EXPLORER ###
    self.ui.actionShowDupeInExplorer      = QtGui.QAction("Show in explorer", None, triggered = (lambda: self.showNodeInExplorer(self.ui.treeDupes.currentItem())))
    self.ui.actionShowSimilarInExplorer   = QtGui.QAction("Show in explorer", None, triggered = (lambda: self.showNodeInExplorer(self.ui.treeSimilar.currentItem())))
    self.ui.actionShowReferenceInExplorer = QtGui.QAction("Show in explorer", None, triggered = (lambda: self.showNodeInExplorer(self.ui.treeReferences.currentItem())))
    self.ui.treeDupes     .addAction(self.ui.actionShowDupeInExplorer)
    self.ui.treeSimilar   .addAction(self.ui.actionShowSimilarInExplorer)
    self.ui.treeReferences.addAction(self.ui.actionShowReferenceInExplorer)
    
    ### SEPARATOR ###
    self.ui.treeDupes     .addAction(self.ui.actionSeparator2)
    self.ui.treeSimilar   .addAction(self.ui.actionSeparator2)
    self.ui.treeReferences.addAction(self.ui.actionSeparator2)
    
    ### DUPES/SIMILARITY STUFF ###
    self.ui.actionAddDupeSim        = QtGui.QAction("Mark as duplicate", None, triggered = (lambda: self.addDupe(self.ui.treeSimilar.currentItem())))
    self.ui.actionAddDupeRef        = QtGui.QAction("Mark as duplicate", None, triggered = (lambda: self.addDupe(self.ui.treeReferences.currentItem())))
    self.ui.actionRemoveSimilarity  = QtGui.QAction("Remove similarity", None, triggered = self.removeSimilarityMenu)
    self.ui.actionRemoveDupeRelated = QtGui.QAction("Remove duplicate",  None, triggered = self.removeDupeRelated)
    self.ui.actionRemoveDupeAll     = QtGui.QAction("Remove all duplicates", None, triggered = self.removeDupeAll)
    self.ui.treeDupes     .addAction(self.ui.actionRemoveDupeRelated)
    self.ui.treeDupes     .addAction(self.ui.actionRemoveDupeAll)
    self.ui.treeSimilar   .addAction(self.ui.actionAddDupeSim)
    self.ui.treeSimilar   .addAction(self.ui.actionRemoveSimilarity)
    self.ui.treeReferences.addAction(self.ui.actionAddDupeRef)
    
    ### SCRIPT FILES TREE ###
    #self.ui.actionInsertLine        = QtGui.QAction("Insert line after selection", None, triggered = self.insertLine)
    self.ui.actionInsertLine.triggered.connect(self.insertLine)
    self.ui.actionRemoveDupeActive  = QtGui.QAction("Remove from duplicate group",  None, triggered = self.removeDupeActive)
    self.ui.lstFiles.addAction(self.ui.actionInsertLine)
    self.ui.lstFiles.addAction(self.ui.actionRemoveDupeActive)
    
    ##############################
    ### MENU BAR ACTIONS
    ##############################
    self.ui.actionCopyOrig.triggered.connect(self.copyFromOrig)
    
    self.ui.actionOpen.triggered.connect(self.showOpenMenu)
    self.ui.actionGoToReference.triggered.connect(self.showGotoMenu)
    self.ui.actionSave.triggered.connect(self.saveChanges)
    self.ui.actionExit.triggered.connect(self.close)
    self.ui.actionReloadDirectory.triggered.connect(self.reloadDirectory)
    
    self.ui.actionTerminology.triggered.connect(self.showTerminologyEditor)
    self.ui.actionConsole.triggered.connect(self.console.show)
    self.ui.actionScriptDumper.triggered.connect(self.showScriptDumper)
    
    self.ui.actionBuild.triggered             .connect(self.buildArchives)
    self.ui.actionSearch.triggered            .connect(self.showSearchMenu)
    self.ui.actionShowPrefs.triggered         .connect(self.showSettingsMenu)
    self.ui.actionCalculateProgress.triggered .connect(self.showProgressCalculator)
    self.ui.actionAbout.triggered             .connect(self.showAbout)
    
    self.ui.actionImportData01.triggered.connect(self.importData01)
    self.ui.actionExportData01.triggered.connect(self.exportData01)
    
    self.ui.actionFirstFile.triggered.connect(self.firstFile)
    self.ui.actionPreviousFile.triggered.connect(self.prevFile)
    self.ui.actionNextFile.triggered.connect(self.nextFile)
    self.ui.actionLastFile.triggered.connect(self.lastFile)
    
    self.ui.actionHighlightTerminology.triggered.connect(self.toggleHighlight)
    self.ui.actionAutoExpand.triggered          .connect(self.updateConfig)
    self.ui.actionAutoPlayVoice.triggered       .connect(self.updateConfig)
    
    self.ui.actionShowDirectory.triggered .connect(self.showCurrentInExplorer)
    self.ui.actionReloadDupesDB.triggered .connect(self.reloadDupes)
    self.ui.actionCheckForErrors.triggered.connect(self.checkForErrors)
    self.ui.actionFontGenerator.triggered .connect(self.showFontGenerator)
    
    ##############################
    ### SIGNALS
    ##############################
    self.ui.txtComments.refs_edited.connect(self.updateRefs)
    
    self.ui.btnAddSingleQuotes.clicked.connect(lambda: self.surroundSelection(u"‘", u"’"))
    self.ui.btnAddQuotes.clicked.connect(lambda: self.surroundSelection(u"“", u"”"))
    self.ui.btnAddEnDash.clicked.connect(lambda: self.replaceSelection(u"–"))
    self.ui.btnAddDash.clicked.connect(lambda: self.replaceSelection(u"―"))
    self.ui.btnAddBrackets.clicked.connect(lambda: self.surroundSelection(u"【", u"】"))
    
    add_clt     = lambda: self.surroundSelection((u"<CLT %02d>" % self.ui.spnClt.value()), u"<CLT>")
    add_clt_rev = lambda: self.surroundSelection(u"<CLT>", (u"<CLT %02d>" % self.ui.spnClt.value()))
    self.ui.btnAddClt.clicked.connect(add_clt)
    self.ui.btnAddClt.rightClicked.connect(add_clt_rev)
    self.ui.actionInsertCLT.triggered.connect(add_clt)
    
    # self.ui.shortcutAddClt = QShortcut(QKeySequence("Ctrl+Alt+C"), self.ui.txtTranslated)
    # self.ui.shortcutAddClt.activated.connect(lambda: self.surroundSelection((u"<CLT %d>" % self.ui.spnClt.value()), u"<CLT>"))
    # self.ui.shortcutAddCltReversed = QShortcut(QKeySequence("Ctrl+Alt+Shift+C"), self.ui.txtTranslated)
    # self.ui.shortcutAddCltReversed.activated.connect(lambda: self.surroundSelection(u"<CLT>", (u"<CLT %d>" % self.ui.spnClt.value())))
    
    self.ui.shortcutCltUp   = QShortcut(QKeySequence("Ctrl++"), self)
    self.ui.shortcutCltDown = QShortcut(QKeySequence("Ctrl+-"), self)
    self.ui.shortcutCltUp.activated.connect(lambda: self.ui.spnClt.setValue(self.ui.spnClt.value() + 1))
    self.ui.shortcutCltDown.activated.connect(lambda: self.ui.spnClt.setValue(self.ui.spnClt.value() - 1))
    
    ##############################
    ### TOOLBAR STUFF
    ##############################
    toolbar_spacer = QtGui.QWidget()
    toolbar_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
    self.ui.toolBar.addWidget(toolbar_spacer)
    
    # Right-aligned actions
    self.ui.toolBar.addAction(self.ui.actionCalculateProgress)
    self.ui.toolBar.addAction(self.ui.actionCheckForErrors)
    self.ui.toolBar.addAction(self.ui.actionBuild)
    
    ##############################
    ### STATUS BAR STUFF
    ##############################
    self.ui.statusLabelMode      = QtGui.QLabel("Mode")
    self.ui.statusLabelCursor    = QtGui.QLabel("Cursor info")
    self.ui.statusLabelWordCount = QtGui.QLabel("Word count")
    self.ui.statusLabelDirInfo   = QtGui.QLabel("Dir Info")
    self.ui.statusLabelRelated   = QtGui.QLabel("Related")
    self.ui.statusbar.addWidget(self.ui.statusLabelMode, stretch = 505)
    self.ui.statusbar.addWidget(self.ui.statusLabelCursor, stretch = 342)
    self.ui.statusbar.addWidget(self.ui.statusLabelWordCount, stretch = 114)
    self.ui.statusbar.addWidget(self.ui.statusLabelDirInfo, stretch = 147)
    self.ui.statusbar.addWidget(self.ui.statusLabelRelated, stretch = 320)
    
    ##############################
    ### MISC
    ##############################
    self.voice_player = VoicePlayer()
    self.ui.volumeSlider.setAudioOutput(self.voice_player.output)
    # self.ui.barVoiceVolume.valueChanged.connect(lambda value: self.voice_player.set_volume(value / 100.0))
    
    # self.bgm_player = BGMPlayer()
    # self.ui.barBGMVolume.valueChanged.connect(lambda value: self.bgm_player.set_volume(value / 100.0))
    
    self.hide_original = False
    
    self.updateActions()
    self.loadDirectory(common.editor_config.last_opened)
    
    self.search_menu = SearchMenu()
    self.search_menu.open_clicked.connect(self.searchMenuOpenClicked)
    self.open_menu = OpenMenu(self, self.directory)
    
    self.progress_calc = ProgressCalculator()
    self.terminology_editor = TerminologyEditor()
    self.font_gen_menu = FontGenMenu()
  
  ##############################################################################
  ### @fn   updateActions()
  ### @desc Takes values from the config file and updates UI elements to match.
  ##############################################################################
  def updateActions(self):
    self.ui.actionHighlightTerminology.setChecked(common.editor_config.highlight_terms)
    self.ui.actionAutoExpand.setChecked(common.editor_config.auto_expand)
    self.ui.actionAutoPlayVoice.setChecked(common.editor_config.auto_play_voice)
  
  ##############################################################################
  ### @fn   updateConfig()
  ### @desc Takes setting changes made on the UI and update the config file.
  ##############################################################################
  def updateConfig(self):
    common.editor_config.highlight_terms = self.ui.actionHighlightTerminology.isChecked()
    common.editor_config.auto_expand = self.ui.actionAutoExpand.isChecked()
    common.editor_config.auto_play_voice = self.ui.actionAutoPlayVoice.isChecked()
    common.editor_config.last_opened = self.directory
    
    common.editor_config.save_config()
  
  ##############################################################################
  ### @fn   loadDirectory(directory)
  ### @desc Parses and loads a directory with script files.
  ##############################################################################
  def loadDirectory(self, directory, clear_similarity = True, selected_file = None):
    
    directory = dir_tools.normalize(directory)
    
    # Record our last selected file before we leave this directory.
    if not self.directory == "":
      self.recordSelectedFile()
    
    # See if we're trying to load a special kind of directory.
    if directory[:7] == "anagram":
      self.loadAnagram(directory)
      return
    
    elif directory[:7] == "nonstop" or directory[:6] == "hanron" or directory[:6] == "kokoro":
      parser = NonstopParser()
      parser.load(directory)
      self.script_pack = parser.script_pack
      
      # No, you can't insert lines into the nonstop debates. (ノ｀Д´)ノ彡┻━┻
      self.ui.actionInsertLine.setEnabled(False)
    
    elif directory[:8] == "hs_mtb_s" or directory[:10] == "dr2_mtb2_s":
      parser = MTBParser()
      parser.load(directory)
      self.script_pack = parser.script_pack
      
      # No, you can't insert lines into the MTBs either.
      self.ui.actionInsertLine.setEnabled(False)
    
    else:
      try:
        script_pack = ScriptPack(directory, common.editor_config.data01_dir)
      except Exception as e:
        QtGui.QMessageBox.critical(self, "Error", str(e))
        return
      else:
        if len(script_pack) <= 0:
          QtGui.QMessageBox.warning(self, "No Lines", "Could not load %s. No lines found." % directory)
          return
        
        self.script_pack = script_pack
        
        if not self.script_pack.wrd_file == None:
          self.ui.actionInsertLine.setEnabled(True)
        else:
          self.ui.actionInsertLine.setEnabled(False)
        
    # So we don't trigger any play commands while loading.
    temp_auto_voice = common.editor_config.auto_play_voice
    common.editor_config.auto_play_voice = False
    
    # If we weren't given a file to start out on, see if we have something
    # we can use before we go inserting the files, which will toss up our data.
    if selected_file == None and directory in common.editor_config.last_file:
      selected_file = common.editor_config.last_file[directory]
    
    self.cur_script = 0
    
    self.changed = [False] * len(self.script_pack)
    
    self.ui.lstFiles.clear()
    self.ui.lblFolderName.setText(directory)
    self.directory = directory
    
    # Getting to be a bit of a memory whore if we leave the data around too long.
    # if clear_similarity:
      # self.similarity_db.clear()
    self.similarity_db.clear_queue()
    
    # Reversed so we can add to the Similarity DB simultaneously. We want the
    # queries at the the top, but in reverse order, so we prioritize finding data
    # about the folder we're currently editing, but still go from the top down.
    for script in reversed(self.script_pack):
      basename = os.path.basename(script.filename)
      
      # Add our easy to read name to the main list.
      self.ui.lstFiles.insertItem(0, QtGui.QListWidgetItem(basename))
      self.similarity_db.queue_query_at_top(os.path.join(self.script_pack.get_real_dir(), basename))
    
    # We're safe now.
    common.editor_config.auto_play_voice = temp_auto_voice
    
    # Some cleanup.
    self.findInternalDupes()
    self.updateConfig()
    self.setWindowModified(False)
    
    if selected_file == None and self.directory in common.editor_config.last_file:
      selected_file = common.editor_config.last_file[self.directory]
    
    if not selected_file == None:
      self.setCurrentFile(selected_file)
    else:
      self.ui.lstFiles.setCurrentRow(0)
    
    self.updateStatusBar()
  
  ##############################################################################
  ### @fn   setCurrentFile(filename)
  ### @desc Selects the file in the current directory with the given name.
  ##############################################################################
  def setCurrentFile(self, filename):
    nodes = self.ui.lstFiles.findItems(filename, Qt.Qt.MatchFixedString)
    
    if len(nodes) >= 1:
      self.ui.lstFiles.setCurrentItem(nodes[0])
      self.ui.lstFiles.scrollToItem(nodes[0], QtGui.QAbstractItemView.PositionAtCenter)
    else:
      self.ui.lstFiles.setCurrentRow(0)
  
  ##############################################################################
  ### @fn   loadAnagram(anagram)
  ### @desc Shows the anagram editor and hides the main window until it's done.
  ##############################################################################
  def loadAnagram(self, anagram):
    self.hide()
    
    anagram_editor = AnagramEditor()
    path = os.path.join(common.editor_config.data01_dir_jp_all, anagram)
    anagram_editor.load(path)
    anagram_editor.exec_()
    
    self.show()
  
  ##############################################################################
  ### @fn   loadEbootText()
  ### @desc Shows the EBOOT text editor and hides the main window until it's done.
  ##############################################################################
  def loadEbootText(self):
    self.hide()
    
    eboot_editor = EbootEditor()
    eboot_editor.exec_()
    
    self.show()
  
  ##############################################################################
  ### @fn   recordSelectedFile()
  ### @desc Records the currently selected file into our history of selected files.
  ##############################################################################
  def recordSelectedFile(self):
    filename = os.path.basename(self.script_pack[self.cur_script].filename)
    common.editor_config.last_file[self.directory] = filename
  
  ##############################################################################
  ### @fn   insertLine()
  ### @desc Inserts a new line after the selected line.
  ##############################################################################
  def insertLine(self):
    
    # Can't insert without a wrd file.
    if self.script_pack.wrd == None:
      # Shouldn't be enabled anyway, but we'll be safe about it.
      self.ui.actionInsertLine.setEnabled(False)
      return
    
    if not isinstance(self.script_pack[self.cur_script], ScriptFile):
      return
    
    # Make absolutely sure we want to do this.
    # Absolutely sure.
    # Seriously.
    # 真剣で。
    
    answer = QtGui.QMessageBox.warning(
      self,
      "Insert Line",
      "You are about to insert a new line into the script. This action cannot be undone. " + 
      "The added line will not have any similarities or duplicates, as there is no good way to keep track of these things for newly created lines.\n\n"
      "If you made modifications to the decompiled .py file since loading this folder, they will be lost. If you want to keep your changes, click the Reload button and try inserting again.\n\n" +
      "Proceed?",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    if not self.askUnsavedChanges():
      return
    
    dir = os.path.join(self.script_pack.get_real_dir())
    filename = os.path.basename(self.script_pack[self.cur_script].filename)
    filename = os.path.join(dir, filename)
    filename = dir_tools.normalize(filename)
    dupes = dupe_db.files_in_same_group(filename)
    
    if not dupes == None:
      answer = QtGui.QMessageBox.warning(
        self,
        "Insert Line",
        "You are about to insert a new line after a file that has dupes.\n\n" + 
        "This can really screw things up if you're not careful.\n\n" +
        "Proceed?",
        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        defaultButton = QtGui.QMessageBox.No
      )
      
      if answer == QtGui.QMessageBox.No:
        return
    
    # If we're totally sure, then we'll get going.
    # We want the file ID as it's referenced in the wrd file.
    insert_after = self.script_pack[self.cur_script].scene_info.file_id
    
    # Make sure it works, first.
    try:
      # new_wrd, new_index = wrd_inserter.insert_line(wrd_file, insert_after)
      new_index = self.script_pack.wrd.insert_line(insert_after)
    except Exception as e:
      QtGui.QMessageBox.critical(self, "Error", str(e))
      return
    
    # Get our backup out of the way, first.
    source_dir = common.editor_config.data01_dir
    
    wrd_file = self.script_pack.wrd_file
    py_file  = self.script_pack.py_file
    
    wrd_basename = os.path.basename(wrd_file)
    py_basename  = os.path.basename(py_file)
    
    # backup.backup_files(source_dir, [wrd_file[len(source_dir) + 1:], py_file[len(source_dir) + 1:]], suffix = "_NEWLINE")
    backup.backup_files(source_dir, [py_file[len(source_dir) + 1:]], suffix = "_NEWLINE")
    
    changes_dir  = os.path.join(common.editor_config.changes_dir, self.script_pack.get_real_dir())
    original_dir = os.path.join(common.editor_config.data01_dir, self.script_pack.get_real_dir())
    
    # A copy for our change set.
    # changes_wrd = os.path.join(changes_dir, wrd_basename)
    changes_py  = os.path.join(changes_dir, py_basename)
    
    if not os.path.isdir(changes_dir):
      os.makedirs(changes_dir)
    
    # Dump our wrd file to disk.
    # self.script_pack.wrd.save_bin(wrd_file)
    # self.script_pack.wrd.save_bin(changes_wrd)
    
    self.script_pack.wrd.save_python(py_file)
    self.script_pack.wrd.save_python(changes_py)
    
    # Then duplicate the selected file with the new name.
    new_filename = "%04d.txt" % new_index
    
    shutil.copy(self.script_pack[self.cur_script].filename, os.path.join(original_dir, new_filename))
    shutil.copy(self.script_pack[self.cur_script].filename, os.path.join(changes_dir, new_filename))
    
    # Reload the directory, so the changes are visible.
    self.loadDirectory(self.directory, clear_similarity = False, selected_file = os.path.basename(self.script_pack[self.cur_script].filename))
  
  ##############################################################################
  ### @fn   findInternalDupes()
  ### @desc Find duplicates between files in this folder.
  ##############################################################################
  def findInternalDupes(self):
    
    self.internal_dupes = {}
    
    dir = dir_tools.normalize(self.script_pack.get_real_dir())
    
    # So we can get indexes in the script list without a ton of looping.
    name_to_index = {}
    
    for index, script in enumerate(self.script_pack):
      if not isinstance(script, ScriptFile):
        continue
      
      name = os.path.basename(script.filename)
      name_to_index[name] = index
    
    for index, script in enumerate(self.script_pack):
      if not isinstance(script, ScriptFile):
        continue
    
      filename = os.path.basename(script.filename)
      filename = os.path.join(dir, filename)
      filename = dir_tools.normalize(filename)
      
      dupes = dupe_db.files_in_same_group(filename)
      
      self.internal_dupes[index] = []
      
      if dupes == None:
        continue
      
      for dupe in dupes:
        if dupe == filename:
          continue
        
        dupe_dir, dupe_name = os.path.split(dupe)
        
        if dupe_dir == dir and dupe_name in name_to_index:
          self.internal_dupes[index].append(name_to_index[dupe_name])
  
  ##############################################################################
  ### @fn    showImage(image_pos)
  ### @param image_pos -- IMAGE_POS.original or IMAGE_POS.translated
  ###                     If None, will update both images.
  ##############################################################################
  def showImage(self, image_pos = None):
    bg = self.bg
    if bg == None:
      bg = QImage(text_printer.IMG_W, text_printer.IMG_H, QImage.Format_ARGB32_Premultiplied)
      bg.fill(QtGui.QColor(0, 0, 0, 255).rgba())
    
    max = 0
    kill_blanks = True
    
    scene_info = self.script_pack[self.cur_script].scene_info
    format     = TEXT_FORMATS[scene_info.mode] if scene_info.format == None else scene_info.format
    mangle     = common.editor_config.mangle_text
  
    if image_pos == None or image_pos == IMAGE_POS.original:
      if not self.hide_original:
        text = common.qt_to_unicode(self.ui.txtOriginal.toPlainText())
        orig = text_printer.print_text(bg, text, scene_info.mode, format, mangle)
        
        if scene_info.special == common.SCENE_SPECIAL.option:
          orig = text_printer.print_text(orig, text, common.SCENE_SPECIAL.option, TEXT_FORMATS[common.SCENE_SPECIAL.option], mangle)
        
        qt_pixmap = QtGui.QPixmap.fromImage(orig)
        self.ui.lblOriginal.setPixmap(qt_pixmap)
      
      else:
        hidden = QImage(text_printer.IMG_W, text_printer.IMG_H, QImage.Format_ARGB32_Premultiplied)
        hidden.fill(QtGui.QColor(0, 0, 0, 255).rgba())
        qt_pixmap = QtGui.QPixmap.fromImage(hidden)
        self.ui.lblOriginal.setPixmap(qt_pixmap)
    
    if image_pos == None or image_pos == IMAGE_POS.translated:
      text = common.qt_to_unicode(self.ui.txtTranslated.toPlainText())
      trans = text_printer.print_text(bg, text, scene_info.mode, format, mangle)
      
      if scene_info.special == common.SCENE_SPECIAL.option:
        trans = text_printer.print_text(trans, text, common.SCENE_SPECIAL.option, TEXT_FORMATS[common.SCENE_SPECIAL.option], mangle)
        
      qt_pixmap = QtGui.QPixmap.fromImage(trans)
      self.ui.lblTranslated.setPixmap(qt_pixmap)
  
  ##############################################################################
  ### @fn   updateUI()
  ### @desc Matches the UI elements to the selected script data.
  ##############################################################################
  def updateUI(self):
    scene_info = self.script_pack[self.cur_script].scene_info
    
    ###################################################
    ### SPEAKER
    ###################################################
    self.ui.lblSpeaker.setToolTip("Speaker ID: %d" % scene_info.speaker)
    
    speaker = get_char_name(scene_info.speaker, common.editor_config.data01_dir)
    if speaker == None:
      speaker = "N/A"
    self.ui.lblSpeaker.setText(speaker)
    
    ###################################################
    ### SPRITE
    ###################################################
    self.ui.lblSprite.setToolTip("Sprite ID: %d" % scene_info.sprite.sprite_id)
    
    sprite_char = get_char_name(scene_info.sprite.char_id, common.editor_config.data01_dir)
    if sprite_char == None:
      sprite_char = "N/A"
    self.ui.lblSprite.setText(sprite_char)
    
    ###################################################
    ### SCENE INFO
    ###################################################
    scene_text = common.chapter_to_text(scene_info.chapter)
    if not scene_info.scene == -1:
      if scene_info.chapter == common.CHAPTER_FREETIME:
        scene_text += ": " + get_char_name(scene_info.scene, common.editor_config.data01_dir)
      elif scene_info.chapter == common.CHAPTER_ISLAND and scene_info.scene >= 701 and scene_info.scene <= 715:
        scene_text += ": " + get_char_name(scene_info.scene - 700, common.editor_config.data01_dir)
      else:
        scene_text += ", Scene %d" % scene_info.scene
    self.ui.lblScene.setText(scene_text)
    
    self.ui.lblScene.setToolTip("BGD: %d\nCut-in: %d\nFlash: %d\nMovie: %d" % (scene_info.bgd, scene_info.cutin, scene_info.flash, scene_info.movie))
    
    ###################################################
    ### MODE
    ###################################################
    self.ui.lblMode.setText(common.mode_to_text(scene_info.mode))
    
    ###################################################
    ### BOX COLOR
    ###################################################
    # I don't actually know how to figure this out, anyway.
    #self.ui.lblColor.setText(str(scene_info.box_color).title())
    
    ###################################################
    ### MAP
    ###################################################
    map_name = get_map_name(scene_info.room, common.editor_config.data01_dir)
    
    self.ui.lblArea.setToolTip("Area ID: %d" % scene_info.room)
    if not map_name == None:
      self.ui.lblArea.setText(map_name)
    else:
      self.ui.lblArea.setText("N/A")
    
    ###################################################
    ### VOICE
    ###################################################
    voice_tooltip = "Chapter: %d\nCharacter: %d\nVoice ID: %d" % (scene_info.voice.chapter, scene_info.voice.char_id, scene_info.voice.voice_id)
    voice = get_voice_file(scene_info.voice)
    
    if not voice == None:
      voice_char = get_char_name(scene_info.voice.char_id, common.editor_config.data01_dir)
      if voice_char == None:
        voice_char = "N/A"
      
      self.ui.lblVoice.setText(voice_char)
      self.ui.btnPlayVoice.setEnabled(True)
      
      voice_tooltip += "\nFile: %d" % voice
    else:
      self.ui.lblVoice.setText("N/A")
      self.ui.btnPlayVoice.setEnabled(False)
      
    self.ui.lblVoice.setToolTip(voice_tooltip)
    
    ###################################################
    ### BGM
    ###################################################
    # if scene_info.bgm != -1:
      # bgm_tooltip = "BGM ID: %d" % scene_info.bgm
      
      # bgm_name = get_bgm_name(scene_info.bgm, common.editor_config.data01_dir)
      # self.ui.lblBGM.setText(bgm_name)
      # self.ui.btnPlayBGM.setEnabled(True)
    
    # else:
      # bgm_tooltip = "BGM ID: N/A"
      
      # self.ui.lblBGM.setText("N/A")
      # self.ui.btnPlayBGM.setEnabled(False)
      
    # self.ui.lblBGM.setToolTip(bgm_tooltip)
    
    ###################################################
    ### SPECIAL
    ###################################################
    self.ui.lblSpecial.setToolTip("")
    if scene_info.special == common.SCENE_SPECIAL.option:
      self.ui.lblSpecial.setText("Options: %s" % scene_info.extra_val)
    elif scene_info.special == common.SCENE_SPECIAL.showopt:
      self.ui.lblSpecial.setText("Options: %s" % scene_info.extra_val)
    elif scene_info.special == common.SCENE_SPECIAL.react:
      self.ui.lblSpecial.setText("Re:ACT")
    elif scene_info.special == common.SCENE_SPECIAL.debate:
      self.ui.lblSpecial.setText("Nonstop Debate")
    elif scene_info.special == common.SCENE_SPECIAL.hanron:
      self.ui.lblSpecial.setText("Counterstrike Showdown")
    elif scene_info.special == common.SCENE_SPECIAL.chatter:
      self.ui.lblSpecial.setText("Chatter %d" % scene_info.extra_val)
    elif scene_info.special == common.SCENE_SPECIAL.checkobj:
      obj_label = get_obj_label(scene_info.room, scene_info.extra_val - 20, common.editor_config.data01_dir)
      if obj_label:
        self.ui.lblSpecial.setText("Obj: %s" % obj_label)
        self.ui.lblSpecial.setToolTip("Obj ID: %d" % scene_info.extra_val)
      else:
        self.ui.lblSpecial.setText("Obj: ID %d" % scene_info.extra_val)
    elif scene_info.special == common.SCENE_SPECIAL.checkchar:
      character = get_char_name(scene_info.extra_val, common.editor_config.data01_dir)
      if character:
        self.ui.lblSpecial.setText("Char: %s" % character)
        self.ui.lblSpecial.setToolTip("Char ID: %d" % scene_info.extra_val)
      else:
        self.ui.lblSpecial.setText("Char: %s" % scene_info.extra_val)
    else:
      self.ui.lblSpecial.setText("N/A")
  
  ##############################################################################
  ### @fn   showDupes()
  ### @desc Fills in the "Duplicates" tree for this file.
  ##############################################################################
  def showDupes(self):
    
    self.ui.treeDupes.clear()
    
    if not isinstance(self.script_pack[self.cur_script], ScriptFile):
      self.ui.tabRelated.setTabText(0, "0 Dupes")
      return
    
    # A little fiddling with the directory names, since we hide a bunch of info
    # so the UI doesn't get cluttered.
    directory = self.script_pack.get_real_dir()
    filename  = os.path.basename(self.script_pack[self.cur_script].filename)
    filename  = os.path.join(directory, filename)
    filename  = dir_tools.normalize(filename)
    
    dupes = dupe_db.files_in_same_group(filename)
    num_dupes = 0
    
    tree_items = []
    
    if not dupes == None:
      self.ui.actionRemoveDupeActive.setEnabled(True)
      for file in dupes:
        if not file == filename:
          parsed_file = dir_tools.consolidate_dir(file)
          tree_item = tree.path_to_tree(parsed_file)
          tree_items.append(tree_item)
          num_dupes = num_dupes + 1
      
      tree_items = tree.consolidate_tree_items(tree_items)
      
      for item in tree_items:
        self.ui.treeDupes.addTopLevelItem(item)
    
    else:
      self.ui.actionRemoveDupeActive.setEnabled(False)
    
    if num_dupes == 1:
      self.ui.tabRelated.setTabText(0, "%d Dupe" % num_dupes)
    else:
      self.ui.tabRelated.setTabText(0, "%d Dupes" % num_dupes)
    
    # If we refill this, they haven't selected anything and can't mark anything.
    self.ui.actionRemoveDupeRelated.setEnabled(False)
    self.ui.actionRemoveDupeAll.setEnabled(False)
    self.ui.actionShowDupeInEditor.setEnabled(False)
    self.ui.actionShowDupeInExplorer.setEnabled(False)
    
    self.ui.txtSimilarTrans.setPlainText("")
    self.ui.txtSimilarOrig.setPlainText("")
    self.ui.txtSimilarComm.setPlainText("")
    
    if common.editor_config.auto_expand:
      self.ui.treeDupes.expandAll()
  
  ##############################################################################
  ### @fn   showSimilar()
  ### @desc Fills in the "Similar" tree for this file.
  ##############################################################################
  def showSimilar(self):
    
    self.ui.treeSimilar.clear()
    
    if not isinstance(self.script_pack[self.cur_script], ScriptFile):
      self.ui.tabRelated.setTabText(1, "0 Similar")
      return
    
    # A little fiddling with the directory names, since we hide a bunch of info
    # so the UI doesn't get cluttered.
    directory = self.script_pack.get_real_dir()
    filename  = os.path.basename(self.script_pack[self.cur_script].filename)
    filename  = os.path.join(directory, filename)
    filename  = dir_tools.normalize(filename)
    
    num_similar = 0
    tree_items = []
    
    similarities = self.similarity_db.get_similarities(filename)
    
    for file in similarities:
      
      parsed_file = dir_tools.consolidate_dir(file)
      tree_item = tree.path_to_tree(parsed_file)
      tree_items.append(tree_item)
      num_similar = num_similar + 1
  
    tree_items = tree.consolidate_tree_items(tree_items)
  
    for item in tree_items:
      self.ui.treeSimilar.addTopLevelItem(item)
    
    self.ui.tabRelated.setTabText(1, "%d Similar" % num_similar)
    
    # If we refill this, they haven't selected anything and can't mark anything.
    self.ui.actionAddDupeSim.setEnabled(False)
    self.ui.actionRemoveSimilarity.setEnabled(False)
    self.ui.actionShowSimilarInEditor.setEnabled(False)
    self.ui.actionShowSimilarInExplorer.setEnabled(False)
    
    self.ui.txtSimilarTrans.setPlainText("")
    self.ui.txtSimilarOrig.setPlainText("")
    self.ui.txtSimilarComm.setPlainText("")
    
    if common.editor_config.auto_expand:
      self.ui.treeSimilar.expandAll()
  
  ##############################################################################
  ### @fn   updateRefs()
  ### @desc Triggered by a change of references in the comments.
  ##############################################################################
  def updateRefs(self):
  
    self.ui.treeReferences.clear()
    
    if not isinstance(self.script_pack[self.cur_script], ScriptFile):
      self.ui.tabRelated.setTabText(2, "0 References")
      return
      
    # A little fiddling with the directory names, since we hide a bunch of info
    # so the UI doesn't get cluttered.
    directory = self.script_pack.get_real_dir()
    filename  = os.path.basename(self.script_pack[self.cur_script].filename)
    filename  = os.path.join(directory, filename)
    filename  = dir_tools.normalize(filename)
    
    references = self.ui.txtComments.references
    num_refs = 0
    
    tree_items = []
    
    if references:
      for file in references:
        if not file == filename:
          if os.path.split(file)[0] == "":
            file = os.path.join(self.script_pack.directory, file)
          parsed_file = dir_tools.consolidate_dir(file)
          tree_item = tree.path_to_tree(parsed_file)
          tree_items.append(tree_item)
          num_refs = num_refs + 1
      
      tree_items = tree.consolidate_tree_items(tree_items)
      
      for item in tree_items:
        self.ui.treeReferences.addTopLevelItem(item)
    
    if num_refs == 1:
      self.ui.tabRelated.setTabText(2, "%d Reference" % num_refs)
    else:
      self.ui.tabRelated.setTabText(2, "%d References" % num_refs)
    
    # If we refill this, they haven't selected anything and can't mark anything.
    self.ui.actionShowReferenceInEditor.setEnabled(False)
    self.ui.actionShowReferenceInExplorer.setEnabled(False)
    self.ui.actionAddDupeRef.setEnabled(False)
    
    if common.editor_config.auto_expand:
      self.ui.treeReferences.expandAll()
  
  ##############################################################################
  ### @fn   updateSimilarView()
  ### @desc Displays text on the right panel based the selected tree item.
  ##############################################################################
  def updateSimilarView(self, tree_item):
    if tree_item == None or tree_item.childCount() != 0:
      self.ui.actionAddDupeSim.setEnabled(False)
      self.ui.actionAddDupeRef.setEnabled(False)
      self.ui.actionRemoveSimilarity.setEnabled(False)
      self.ui.actionRemoveDupeRelated.setEnabled(False)
      #self.ui.actionRemoveDupeAll.setEnabled(False)
      return
    #else:
      #self.ui.actionAddDupeSim.setEnabled(True)
      #self.ui.actionRemoveSimilarity.setEnabled(True)
      #self.ui.actionRemoveDupeRelated.setEnabled(True)
      #self.ui.actionRemoveDupeAll.setEnabled(True)
    
    self.updateStatusRelated()
    
    file         = common.qt_to_unicode(tree_item.text(0))
    directory    = tree.tree_item_to_path(tree_item.parent())
    expanded_dir = dir_tools.expand_dir(directory)
    
    filename = os.path.join(common.editor_config.data01_dir, expanded_dir, file)
    
    if not os.path.isfile(filename):
      self.ui.txtSimilarTrans.setPlainText("Could not load \"%s\"." % file)
      self.ui.txtSimilarOrig.setPlainText("")
      self.ui.txtSimilarComm.setPlainText("")
      
      self.ui.actionAddDupeSim.setEnabled(False)
      self.ui.actionAddDupeRef.setEnabled(False)
      return
    
    if not directory == self.directory:
      script_file = ScriptFile(filename)
    else:
      script_file = self.script_pack.get_script(file)
      
      # If a file exists in this directory but, for some reason
      # isn't referenced in the wrd file, so it's not in the
      # script pack, just load it anyway, so we can see it.
      if script_file == None:
        script_file = ScriptFile(filename)
    
    self.ui.txtSimilarTrans.setPlainText(script_file[common.editor_config.lang_trans])
    self.ui.txtSimilarOrig.setPlainText(script_file[common.editor_config.lang_orig])
    self.ui.txtSimilarComm.setPlainText(script_file.comments)
  
  ##############################################################################
  ###                                                                        ###
  ###                                S L O T S                               ###
  ###                                                                        ###
  ##############################################################################
  
  ##############################################################################
  ### @fn   showOpenMenu()
  ### @desc Two guesses.
  ##############################################################################
  def showOpenMenu(self):
    self.open_menu.exec_()
    
    # If they chose something, and there are unsaved changes,
    # ask about them before trying to load the folder.
    if not self.open_menu.current_dir == None \
       and not dir_tools.normalize(self.directory) == dir_tools.normalize(self.open_menu.current_dir) \
       and self.askUnsavedChanges():
      self.loadDirectory(self.open_menu.current_dir)
  
  ##############################################################################
  ### @fn   showGotoMenu()
  ### @desc Two and a half guesses.
  ##############################################################################
  def showGotoMenu(self):
    
    reference, accepted = QtGui.QInputDialog.getText(self, "Go to...", "Where would you like to go?")
    if not accepted:
      return
    
    reference = common.qt_to_unicode(reference)
    reference = re.sub(ur"[{}]", u"", reference)
    
    if not reference:
      return
    
    directory, filename = os.path.split(reference)
    
    if not directory and not filename:
      return
    elif not directory:
      directory = filename
      filename  = None
    elif not filename:
      filename  = None
      
    if not dir_tools.normalize(directory) == dir_tools.normalize(self.directory):
      if not self.askUnsavedChanges():
        return
      self.loadDirectory(directory, selected_file = filename)
    
    else:
      self.setCurrentFile(filename)
  
  ##############################################################################
  ### @fn   gotoScriptJump()
  ### @desc Go to the folder indicated by the ScriptJump object currently selected.
  ##############################################################################
  def gotoScriptJump(self):
    if not isinstance(self.script_pack[self.cur_script], ScriptJump):
      return
    
    target = self.script_pack[self.cur_script].target()
    
    if not dir_tools.normalize(target) == dir_tools.normalize(self.directory):
      if not self.askUnsavedChanges():
        return
      self.loadDirectory(target)
    
  ##############################################################################
  ### @fn   showSettingsMenu()
  ### @desc Three guesses.
  ##############################################################################
  def showSettingsMenu(self):
    # Store this so we can see if they changed anything.
    temp_data01 = common.editor_config.data01_dir
    
    menu = SettingsMenu(self)
    result = menu.exec_()
    
    self.showImage()
    self.updateActions()
    self.updateHighlight()
    self.updateTranslatedBoxCfg()
    
    # If they changed data01, reload the directory,
    # so we're looking at the one they're actually set to use.
    if not dir_tools.normalize(temp_data01) == dir_tools.normalize(common.editor_config.data01_dir):
      self.askUnsavedChanges()
      self.loadDirectory(self.directory, clear_similarity = False, selected_file = os.path.basename(self.script_pack[self.cur_script].filename))
    
  ##############################################################################
  ### @fn   showProgressCalculator()
  ### @desc Three and a third guesses.
  ##############################################################################
  def showProgressCalculator(self):
    self.progress_calc.show()
    self.progress_calc.raise_()
    self.progress_calc.activateWindow()
    
  ##############################################################################
  ### @fn   showSearchMenu()
  ### @desc Four guesses.
  ##############################################################################
  def showSearchMenu(self):
    self.search_menu.show()
    self.search_menu.raise_()
    self.search_menu.activateWindow()
  
  ##############################################################################
  ### @fn   searchMenuOpenClicked()
  ### @desc Four and a quarter guesses.
  ##############################################################################
  def searchMenuOpenClicked(self):
    node = self.search_menu.ui.treeResults.currentItem()
    if node == None:
      return
    
    self.showNodeInEditor(self.search_menu.ui.treeResults.currentItem())
    self.raise_()
    self.activateWindow()
    
  ##############################################################################
  ### @fn   showTerminologyEditor()
  ### @desc Four AND A HALF guesses.
  ##############################################################################
  def showTerminologyEditor(self):
    self.terminology_editor.show()
    self.terminology_editor.raise_()
    self.terminology_editor.activateWindow()
  
  ##############################################################################
  ### @fn   showFontGenerator()
  ### @desc X guesses.
  ##############################################################################
  def showFontGenerator(self):
    self.font_gen_menu.show()
    self.font_gen_menu.raise_()
    self.font_gen_menu.activateWindow()
  
  ##############################################################################
  ### @fn   showScriptDumper()
  ### @desc X guesses.
  ##############################################################################
  def showScriptDumper(self):
    menu = ScriptDumpMenu(self)
    menu.exec_()
  
  ##############################################################################
  ### @fn   reloadDirectory()
  ### @desc Five guesses.
  ##############################################################################
  def reloadDirectory(self):
    if self.askUnsavedChanges():
      self.loadDirectory(self.directory, clear_similarity = False, selected_file = os.path.basename(self.script_pack[self.cur_script].filename))
  
  ##############################################################################
  ### @fn   saveChanges()
  ### @desc Six guesses.
  ##############################################################################
  def saveChanges(self):
    
    progress = QProgressDialog("Saving...", QString(), 0, len(self.script_pack), self)
    progress.setWindowTitle("Saving...")
    progress.setWindowModality(Qt.Qt.WindowModal)
    progress.setValue(0)
    progress.setAutoClose(False)
    progress.setMinimumDuration(1000)
    
    width = self.width()
    height = self.height()
    x = self.x()
    y = self.y()
  
    dir = self.script_pack.get_real_dir()
    
    # The base name of all the files being saved.
    files   = []
    
    file_count = 0
    
    # Get a list of the files we are going to change.
    for index, script in enumerate(self.script_pack):
      
      files.append([])
      
      # Don't bother if we haven't changed this file.
      if not self.changed[index]:
        continue
      
      # Or if this isn't actually a script file.
      if not isinstance(script, ScriptFile):
        continue
    
      filename = os.path.basename(script.filename)
      filename = os.path.join(dir, filename)
      filename = dir_tools.normalize(filename)
      
      dupes = dupe_db.files_in_same_group(filename)
      
      if dupes == None:
        files[-1].append(filename)
        file_count += 1
        continue
      
      # This includes the original file itself.
      for dupe in dupes:
        files[-1].append(dupe)
        file_count += 1
    
    progress.setMaximum(file_count)
    
    # Make backups first.
    backup_time = time.strftime("%Y.%m.%d_%H.%M.%S_SAVE")
    for file_set in files:
      for file in file_set:
        source = os.path.join(common.editor_config.data01_dir, file)
        target = os.path.join(common.editor_config.backup_dir, backup_time, file)
        
        progress.setLabelText("Backing up...\n" + file)
        progress.setValue(progress.value() + 1)
        
        # Re-center the dialog.
        progress_w = progress.geometry().width()
        progress_h = progress.geometry().height()
        
        new_x = x + ((width - progress_w) / 2)
        new_y = y + ((height - progress_h) / 2)
        
        progress.move(new_x, new_y)
        
        # Make sure we have a place to put it.
        basedir = os.path.dirname(target)
        if not os.path.isdir(basedir):
          os.makedirs(basedir)
        
        shutil.copy2(source, target)
    
    progress.setValue(0)
    
    # Now do some saving.
    for index, script in enumerate(self.script_pack):
      
      file_set = files[index]
      
      for file in file_set:
        
        target      = os.path.join(common.editor_config.data01_dir, file)
        target_copy = os.path.join(common.editor_config.changes_dir, file)
        
        progress.setLabelText("Saving...\n" + file)
        progress.setValue(progress.value() + 1)
        
        # Re-center the dialog.
        progress_w = progress.geometry().width()
        progress_h = progress.geometry().height()
        
        new_x = x + ((width - progress_w) / 2)
        new_y = y + ((height - progress_h) / 2)
        
        progress.move(new_x, new_y)
        
        # Make sure we have a place to put it.
        basedir = os.path.dirname(target_copy)
        if not os.path.isdir(basedir):
          os.makedirs(basedir)
        
        script.save(target)
        script.save(target_copy)
    
    progress.close()
    
    self.setWindowModified(False)
    
    self.changed = [False] * len(self.script_pack)
  
  ##############################################################################
  ### @fn     askUnsavedChanges()
  ### @desc   Checks for unsaved changes, then asks the user how to proceed.
  ### @return Returns True if it is okay to proceed and False if not.
  ##############################################################################
  def askUnsavedChanges(self):
    if not self.isWindowModified():
      return True
    
    answer = QtGui.QMessageBox.question(
      self,
      "Unsaved Changes",
      "Would you like to save your changes?",
      buttons = QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel,
      defaultButton = QtGui.QMessageBox.Cancel
    )
    
    if answer == QtGui.QMessageBox.Cancel:
      return False
    elif answer == QtGui.QMessageBox.Discard:
      return True
    elif answer == QtGui.QMessageBox.Save:
      self.saveChanges()
      return True
  
  ##############################################################################
  ### @fn   playVoice()
  ### @desc Triggered by the "Play Voice" button.
  ##############################################################################
  def playVoice(self):
    self.voice_player.play(self.script_pack[self.cur_script].scene_info.voice)
  
  ##############################################################################
  ### @fn   stopVoice()
  ### @desc Triggered by the "Stop Voice" button.
  ##############################################################################
  def stopVoice(self):
    self.voice_player.stop()
  
  ##############################################################################
  ### @fn   playBGM()
  ### @desc Triggered by the "Play BGM" button.
  ##############################################################################
  # def playBGM(self):
    # self.bgm_player.play(self.script_pack[self.cur_script].scene_info.bgm)
  
  ##############################################################################
  ### @fn   stopBGM()
  ### @desc Triggered by the "Stop BGM" button.
  ##############################################################################
  # def stopBGM(self):
    # self.bgm_player.stop()
  
  ##############################################################################
  ### @fn   updateStatusBar()
  ### @desc Updates all the labels in the status bar.
  ##############################################################################
  def updateStatusBar(self):
    self.updateStatusMode()
    self.updateStatusCursor()
    self.updateStatusWordCount()
    self.updateStatusDirInfo()
    self.updateStatusRelated()
  
  ##############################################################################
  ### @fn   updateStatusMode()
  ### @desc Updates the label on the status bar for the script mode.
  ##############################################################################
  def updateStatusMode(self):
    self.ui.statusLabelMode.setText(common.mode_to_text(self.script_pack[self.cur_script].scene_info.mode))
    
  ##############################################################################
  ### @fn   updateStatusCursor()
  ### @desc Updates the label on the status bar for the text box.
  ##############################################################################
  def updateStatusCursor(self):
    cursor = self.ui.txtTranslated.textCursor()
    
    len       = self.ui.txtTranslated.toPlainText().length()
    lines     = self.ui.txtTranslated.document().blockCount()
    line_num  = cursor.blockNumber() + 1
    col       = cursor.positionInBlock()
    
    # We don't want our column count to include CLTs, so we can actually
    # have a useful look at how long the lines are. So we search for all
    # CLTs on the line we're in that start before the cursor position and
    # we chop them out of the column count.
    line      = common.qt_to_unicode(cursor.block().text())
    tag_re    = TAG_KILLER
    
    adjusted_col = col
    
    for match in tag_re.finditer(line):
      if match.end() <= col:
        adjusted_col -= (match.end() - match.start())
      
      elif match.start() < col:
        adjusted_col -= (col - match.start())
        break
      
      else:
        break
    
    self.ui.statusLabelCursor.setText("Length: %d\t Lines: %d\t Line: %d\t Col: %d" % (len, lines, line_num, adjusted_col))
  
  ##############################################################################
  ### @fn   updateStatusWordCount()
  ### @desc Updates the label on the status bar for the text box.
  ##############################################################################
  def updateStatusWordCount(self):
    words = count_words(common.qt_to_unicode(self.ui.txtTranslated.toPlainText()))
    self.ui.statusLabelWordCount.setText("Words: %d" % words)
  
  ##############################################################################
  ### @fn   updateStatusDirInfo()
  ### @desc Updates the label on the status bar for the directory listing.
  ##############################################################################
  def updateStatusDirInfo(self):
    self.ui.statusLabelDirInfo.setText("Item: %d / %d" % (self.cur_script + 1, len(self.script_pack.script_files)))
  
  ##############################################################################
  ### @fn   updateStatusRelated()
  ### @desc Updates the label on the status bar for the related window.
  ##############################################################################
  def updateStatusRelated(self):
    tree_item = self.ui.treeDupes.currentItem()
    
    if tree_item != None and tree_item.childCount() == 0:
      self.ui.statusLabelRelated.setText("Duplicate: %s" % tree.tree_item_to_path(tree_item))
      return
    
    tree_item = self.ui.treeSimilar.currentItem()
    
    if tree_item != None and tree_item.childCount() == 0:
      self.ui.statusLabelRelated.setText("Similarity: %s" % tree.tree_item_to_path(tree_item))
      return
    
    tree_item = self.ui.treeReferences.currentItem()
    
    if tree_item != None and tree_item.childCount() == 0:
      self.ui.statusLabelRelated.setText("Reference: %s" % tree.tree_item_to_path(tree_item))
      return
    
    self.ui.statusLabelRelated.setText("Nothing selected")
  
  ##############################################################################
  ### @fn   changedOriginalTab()
  ### @desc Called when the tab showing the original text is changed.
  ##############################################################################
  def changedOriginalTab(self):
    hide_original = False
    
    if self.ui.tabsOriginal.currentWidget() == self.ui.tabHide:
      hide_original = True
    
    if self.hide_original != hide_original:
      self.hide_original = hide_original
      self.showImage(IMAGE_POS.original)
  
  ##############################################################################
  ### @fn   changedTranslated()
  ### @desc Called when txtTranslated is changed. Updates the internal script
  ###       information and the preview image.
  ##############################################################################
  def changedTranslated(self):
    if not isinstance(self.script_pack[self.cur_script], ScriptFile):
      self.showImage(IMAGE_POS.translated)
      return
    
    translated = common.qt_to_unicode(self.ui.txtTranslated.toPlainText())
    
    if not translated == self.script_pack[self.cur_script][common.editor_config.lang_trans]:
      self.setWindowModified(True)
      self.script_pack[self.cur_script][common.editor_config.lang_trans] = translated
      
      self.changed[self.cur_script] = True
      
      for dupe in self.internal_dupes[self.cur_script]:
        self.script_pack[dupe][common.editor_config.lang_trans] = translated
        #self.changed[dupe] = True
    
    self.showImage(IMAGE_POS.translated)
    
    self.updateStatusCursor()
    self.updateStatusWordCount()
  
  ##############################################################################
  ### @fn   changedOriginal()
  ### @desc Called when txtOriginal is changed. Updates the preview image.
  ##############################################################################
  def changedOriginal(self):
    self.showImage(IMAGE_POS.original)
  
  ##############################################################################
  ### @fn   changedComments()
  ### @desc Called when txtComments is changed. Updates the internal script.
  ##############################################################################
  def changedComments(self):
    if not isinstance(self.script_pack[self.cur_script], ScriptFile):
      return
    
    comments = common.qt_to_unicode(self.ui.txtComments.toPlainText())
    
    if not comments == self.script_pack[self.cur_script].comments:
      self.setWindowModified(True)
      self.script_pack[self.cur_script].comments = comments
      
      self.changed[self.cur_script] = True
      
      for dupe in self.internal_dupes[self.cur_script]:
        self.script_pack[dupe].comments = comments
    
  ##############################################################################
  ### @fn   changedScriptFile(index)
  ### @desc Called when the selected script file is changed. Fills in the text
  ###       boxes and updates the preview images.
  ##############################################################################
  # Find sequential, valid <CLT> tags, with or without numbers, at the end of the line.
  CURSOR_RE = re.compile(ur"(\n*\<CLT(\s+\d+)?\>)*\Z", re.UNICODE)
  
  def changedScriptFile(self, index):
    self.cur_script = index
    
    # Has to happen early, so the highlighter can take advantage of any changes
    # to the terms list as soon as the new text is shown.
    self.updateHighlight()
    self.updateTranslatedBoxCfg()
    
    self.bg = text_printer.draw_scene(self.script_pack[index].scene_info)
    
    self.ui.txtComments.setPlainText(self.script_pack[index].comments)
    self.ui.txtTranslated.setPlainText(self.script_pack[index][common.editor_config.lang_trans])
    
    cursor_match = self.CURSOR_RE.search(self.script_pack[index][common.editor_config.lang_trans])
    
    if cursor_match == None:
      self.ui.txtTranslated.moveCursor(QTextCursor.End)
    else:
      cursor = self.ui.txtTranslated.textCursor()
      cursor.setPosition(cursor_match.start())
      self.ui.txtTranslated.setTextCursor(cursor)
    
    self.ui.txtComments.moveCursor(QTextCursor.End)
    
    self.ui.txtOriginal.setPlainText(self.script_pack[index][common.editor_config.lang_orig])
    self.ui.txtOriginalNoTags.setPlainText(self.script_pack[index].notags[common.editor_config.lang_orig])
    
    if isinstance(self.script_pack[self.cur_script], ScriptJump):
      self.ui.txtTranslated.setReadOnly(True)
      self.ui.txtComments.setReadOnly(True)
      self.ui.actionCopyActivePath.setEnabled(False)
      self.ui.actionGotoScriptJump.setEnabled(True)
      
      self.setWindowTitle("The Super Duper Script Editor 2 - %s[*]" % self.script_pack.directory)
    
    elif isinstance(self.script_pack[self.cur_script], ScriptFile):
      self.ui.txtTranslated.setReadOnly(False)
      self.ui.txtComments.setReadOnly(False)
      self.ui.actionCopyActivePath.setEnabled(True)
      self.ui.actionGotoScriptJump.setEnabled(False)
      
      filename = os.path.basename(self.script_pack[self.cur_script].filename)
      self.setWindowTitle("The Super Duper Script Editor 2 - " + os.path.join(self.script_pack.directory, filename) + "[*]")
    
    #self.showImage()
    
    self.showSimilar()
    self.showDupes()
    
    self.ui.txtSimilarTrans.setPlainText("")
    self.ui.txtSimilarOrig.setPlainText("")
    self.ui.txtSimilarComm.setPlainText("")
    
    self.updateUI()
    self.updateStatusDirInfo()
    self.updateStatusRelated()
    
    if common.editor_config.auto_play_voice:
      self.playVoice()
    
    # if self.script_pack[index].scene_info.bgm < 0:
      # self.stopBGM()
    # else:
      # if common.editor_config.auto_play_bgm:
        # self.playBGM()
    
  ##############################################################################
  ### @fn   changedDupe(current, prev)
  ### @desc Called when the selected dupe is changed. Loads and displays the
  ###       text in the right panel.
  ##############################################################################
  def changedDupe(self, current, prev):
    if current == None:
      self.ui.actionShowDupeInEditor.setEnabled(False)
      self.ui.actionShowDupeInExplorer.setEnabled(False)
      self.ui.actionRemoveDupeRelated.setEnabled(False)
      self.ui.actionRemoveDupeAll.setEnabled(False)
      return
      
    else:
      self.ui.actionShowDupeInEditor.setEnabled(True)
      self.ui.actionShowDupeInExplorer.setEnabled(True)
      self.ui.actionRemoveDupeRelated.setEnabled(True)
      self.ui.actionRemoveDupeAll.setEnabled(True)
    
    self.ui.treeSimilar.setCurrentItem(None)
    self.ui.treeReferences.setCurrentItem(None)
    self.updateSimilarView(current)
  
  ##############################################################################
  ### @fn   changedSimilar(current, prev)
  ### @desc Called when the selected similar file is changed. Loads and
  ###       displays the text in the right panel.
  ##############################################################################
  def changedSimilar(self, current, prev):
    if current == None:
      self.ui.actionShowSimilarInEditor.setEnabled(False)
      self.ui.actionShowSimilarInExplorer.setEnabled(False)
      self.ui.actionAddDupeSim.setEnabled(False)
      self.ui.actionRemoveSimilarity.setEnabled(False)
      return
    
    else:
      self.ui.actionShowSimilarInEditor.setEnabled(True)
      self.ui.actionShowSimilarInExplorer.setEnabled(True)
      self.ui.actionAddDupeSim.setEnabled(True)
      self.ui.actionRemoveSimilarity.setEnabled(True)
    
    self.ui.treeDupes.setCurrentItem(None)
    self.ui.treeReferences.setCurrentItem(None)
    self.updateSimilarView(current)
  
  ##############################################################################
  ### @fn   changedReference(current, prev)
  ### @desc Called when the selected reference file is changed. Loads and
  ###       displays the text in the right panel.
  ##############################################################################
  def changedReference(self, current, prev):
    if current == None:
      self.ui.actionShowReferenceInEditor.setEnabled(False)
      self.ui.actionShowReferenceInExplorer.setEnabled(False)
      self.ui.actionAddDupeRef.setEnabled(False)
      return
    
    else:
      self.ui.actionShowReferenceInEditor.setEnabled(True)
      self.ui.actionShowReferenceInExplorer.setEnabled(True)
      self.ui.actionAddDupeRef.setEnabled(True)
    
    self.ui.treeDupes.setCurrentItem(None)
    self.ui.treeSimilar.setCurrentItem(None)
    self.updateSimilarView(current)
  
  ##############################################################################
  ### @fn   addDupe()
  ### @desc Marks the selected "similar" file as a duplicate of the currently
  ###       active script file and removes it from the similarity database.
  ##############################################################################
  def addDupe(self, node):
    #current = self.ui.treeSimilar.currentItem()
    current = node
    
    if current == None or current.childCount() != 0:
      return
    
    selected_dir  = tree.tree_item_to_path(current.parent())
    selected_dir  = dir_tools.expand_dir(selected_dir)
    selected_dir  = os.path.join(selected_dir)
    selected_file = common.qt_to_unicode(current.text(0))
    selected_file = os.path.join(selected_dir, selected_file)
    
    active_dir  = self.script_pack.get_real_dir()
    active_file = os.path.basename(self.script_pack[self.cur_script].filename)
    active_file = os.path.join(active_dir, active_file)
    active_file = dir_tools.normalize(active_file)
    
    if active_file == selected_file:
      return
    
    active_group = dupe_db.group_from_file(active_file)
    
    # See if this one's in a group. If so, we merge. If not, we add.
    selected_group = dupe_db.group_from_file(selected_file)
    
    # Be sure we actually want to do this.
    if not selected_group == None or not active_group == None:
      answer = QtGui.QMessageBox.warning(
        self,
        "Mark as Duplicate",
        "One or both of the selected files is already a member of a duplicate group.\n\n" +
        "By marking the selected files duplicates, the two duplicate groups will be " + 
        "merged, and all files in both groups will be considered duplicates of each other.\n\n" +
        "Proceed?",
        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        defaultButton = QtGui.QMessageBox.No
      )
      
      if answer == QtGui.QMessageBox.No:
        return
    
    else:
      answer = QtGui.QMessageBox.warning(
        self,
        "Mark as Duplicate",
        "Mark the selected file as a duplicate of the active file?",
        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        defaultButton = QtGui.QMessageBox.No
      )
      
      if answer == QtGui.QMessageBox.No:
        return
    
    self.removeSimilarity(active_file, selected_file)
    
    if active_group == None:
      active_group = dupe_db.add_file(active_file)
    
    if selected_group == None:
      dupe_db.add_file(selected_file, active_group)
    else:
      dupe_db.merge_groups([selected_group, active_group])
    
    dupe_db.save_csv()
    
    self.findInternalDupes()
    self.showSimilar()
    self.showDupes()
  
  ##############################################################################
  ### @fn   removeDupe(filename)
  ### @desc Removes the given file from whatever duplicate group it is in
  ###       and adds it to the similarity database.
  ##############################################################################
  def removeDupe(self, filename):
    
    group = dupe_db.group_from_file(filename)
    
    if group == None:
      return
    
    remaining_files = dupe_db.files_in_group(group)
    remaining_files.discard(filename)
    
    dupe_db.remove_file(filename)
    
    if not remaining_files == None or len(remaining_files) == 0:
      self.similarity_db.add_similar_files([filename], remaining_files, 100)
    
    dupe_db.save_csv()
  
  ##############################################################################
  ### @fn   removeDupeAll()
  ### @desc Kills the entire duplicate group.
  ##############################################################################
  def removeDupeAll(self):
    answer = QtGui.QMessageBox.warning(
      self,
      "Remove Duplicates",
      "Are you sure you want to remove all files from the current duplicate group?\n\n" +
      "All files in this duplicate group will be marked as 100% similar to the each other.\n\n" +
      "This action cannot be undone. Proceed?",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    active_dir  = self.script_pack.get_real_dir()
    active_file = os.path.basename(self.script_pack[self.cur_script].filename)
    active_file = os.path.join(active_dir, active_file)
    active_file = dir_tools.normalize(active_file)
    
    group = dupe_db.group_from_file(active_file)
    
    if group == None:
      return
      
    files = dupe_db.files_in_group(group)
    
    dupe_db.remove_group(group)
    
    # Mark all files as 100% similar to each other.
    self.similarity_db.add_similar_files(files, files, 100)
    
    dupe_db.save_csv()
    
    self.findInternalDupes()
    self.showSimilar()
    self.showDupes()
  
  ##############################################################################
  ### @fn   removeDupeActive()
  ### @desc Removes the active file from its duplicate group.
  ##############################################################################
  def removeDupeActive(self):
    answer = QtGui.QMessageBox.warning(
      self,
      "Remove Duplicate",
      "Are you sure you want to remove the active file from its duplicate group?\n\n" +
      "The active file will be marked as 100% similar to all other files in this duplicate group.",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    active_dir  = self.script_pack.get_real_dir()
    active_file = os.path.basename(self.script_pack[self.cur_script].filename)
    active_file = os.path.join(active_dir, active_file)
    active_file = dir_tools.normalize(active_file)
    
    self.removeDupe(active_file)
    
    self.findInternalDupes()
    self.showSimilar()
    self.showDupes()
  
  ##############################################################################
  ### @fn   removeDupeRelated()
  ### @desc Removes the selected "duplicate" file as a duplicate of the
  ###       currently active script file and adds it to the similarity database.
  ##############################################################################
  def removeDupeRelated(self):
    current = self.ui.treeDupes.currentItem()
    
    if current == None or current.childCount() != 0:
      return
    
    answer = QtGui.QMessageBox.warning(
      self,
      "Remove Duplicate",
      "Are you sure you want to remove the selected file as a duplicate?\n\n" +
      "All other files in this duplicate group will be marked as 100% similar to the selected file.",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    dupe_dir  = tree.tree_item_to_path(current.parent())
    dupe_dir  = dir_tools.expand_dir(dupe_dir)
    dupe_dir  = os.path.join(dupe_dir)
    dupe_file = common.qt_to_unicode(current.text(0))
    dupe_file = os.path.join(dupe_dir, dupe_file)
    
    self.removeDupe(dupe_file)
    
    self.findInternalDupes()
    self.showSimilar()
    self.showDupes()
  
  ##############################################################################
  ### @fn   removeSimilarityMenu()
  ### @desc Removes the selected "similar" file as a similarity of the
  ###       currently active script file.
  ##############################################################################
  def removeSimilarityMenu(self):
    current = self.ui.treeSimilar.currentItem()
    
    if current == None or current.childCount() != 0:
      return
    
    answer = QtGui.QMessageBox.warning(
      self,
      "Remove Similarity",
      "Are you sure you want to remove the selected file as a similarity?\n\n" +
      "All other files in the active file's duplicate group will be marked as non-similar to the selected file.",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    similar_dir  = tree.tree_item_to_path(current.parent())
    similar_dir  = dir_tools.expand_dir(similar_dir)
    similar_dir  = os.path.join(similar_dir)
    similar_file = common.qt_to_unicode(current.text(0))
    similar_file = os.path.join(similar_dir, similar_file)
    
    active_dir  = self.script_pack.get_real_dir()
    active_file = os.path.basename(self.script_pack[self.cur_script].filename)
    active_file = os.path.join(active_dir, active_file)
    active_file = dir_tools.normalize(active_file)
    
    self.removeSimilarity(active_file, similar_file)
    
    self.findInternalDupes()
    self.showSimilar()
    self.showDupes()
  
  ##############################################################################
  ### @fn   removeSimilarity(file1, file2)
  ### @desc Removes any trace of two files being similar to each other.
  ##############################################################################
  def removeSimilarity(self, file1, file2):
    # The similarity data we want to remove in exchange for adding a dupe.    
    # All dupes in the same group store redundant similarity info, so we want
    # to kill all that info in one go.
    file1_dupes = dupe_db.files_in_same_group(file1)
    file2_dupes = dupe_db.files_in_same_group(file2)
    
    if file1_dupes == None:
      file1_dupes = [file1]
    
    if file2_dupes == None:
      file2_dupes = [file2]
    
    self.similarity_db.remove_similar_files(file1_dupes, file2_dupes)
    
  ##############################################################################
  ### @fn   saveImage()
  ### @desc Saves a preview image. :D
  ##############################################################################
  def saveImage(self, image_pos):
  
    dir   = "ss"
    index = 0
    
    if not os.path.isdir(dir):
      if os.path.isfile(dir):
        return
      else:
        os.mkdir(dir)
    
    while True:
      if index >= 9999:
        return
        
      filename = os.path.join(dir, ("shot%04d.png" % index))
      
      if not os.path.isfile(filename):
        break
        
      index = index + 1
    
    if not os.path.isdir(dir):
      os.mkdir(dir)
    
    if image_pos == IMAGE_POS.original:
      self.ui.lblOriginal.pixmap().save(filename)
    elif image_pos == IMAGE_POS.translated:
      self.ui.lblTranslated.pixmap().save(filename)
  
  ##############################################################################
  ### @fn   buildArchives()
  ### @desc Create archives from our data folders.
  ##############################################################################
  def buildArchives(self):
    if not self.askUnsavedChanges():
      return
    
    answer = QtGui.QMessageBox.warning(
      self,
      "Build Archives",
      "Building the archives can take a long time to complete, and once you start the process, it cannot be canceled.\n\n" +
      "Proceed?",
      buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
      defaultButton = QtGui.QMessageBox.No
    )
    
    if answer == QtGui.QMessageBox.No:
      return
    
    # If they happen to close the dialog, then try to build again before it finishes.
    if not self.iso_builder.process == None:
      self.iso_builder.process.kill()
    
    packer = CpkPacker(self)
    packer.create_archives()
    
    if common.editor_config.build_iso:
      self.iso_builder = IsoBuilder(self)
      self.iso_builder.build_iso(common.editor_config.iso_dir, common.editor_config.iso_file)
  
  ##############################################################################
  ### @fn   importData01()
  ### @desc Imports a directory into data01. <3
  ##############################################################################
  def importData01(self):
    return
    
    if not self.askUnsavedChanges():
      return
    
    source_dir = QtGui.QFileDialog.getExistingDirectory(self, caption = "Select a source directory", directory = common.editor_config.last_imported)
    if not source_dir == "":
      source_dir = os.path.abspath(source_dir)
    else:
      return
    
    target_dir  = common.editor_config.data01_dir
    convert     = self.ui.actionConvertPNGGIM.isChecked()
    propogate   = self.ui.actionPropogateDupes.isChecked()
    import_data01(source_dir, target_dir, convert, propogate, parent = self)
    
    common.editor_config.last_imported = source_dir
    common.editor_config.last_import_target = target_dir
    common.editor_config.save_config()
    
    # Reload the directory, so the changes are visible.
    self.loadDirectory(self.directory, clear_similarity = False, selected_file = os.path.basename(self.script_pack[self.cur_script].filename))
  
  ##############################################################################
  ### @fn   exportData01()
  ### @desc Exports data01 to some other directory. <3
  ##############################################################################
  def exportData01(self):
    
    target_dir = QtGui.QFileDialog.getExistingDirectory(self, caption = "Select a target directory", directory = common.editor_config.last_export_target)
    if not target_dir == "":
      target_dir = os.path.abspath(target_dir)
    else:
      return
    
    source_dir  = common.editor_config.data01_dir
    convert     = self.ui.actionConvertPNGGIM.isChecked()
    unique      = self.ui.actionExportUnique.isChecked()
    export_data01(source_dir, target_dir, convert, unique, parent = self)
    
    common.editor_config.last_exported = source_dir
    common.editor_config.last_export_target = target_dir
    common.editor_config.save_config()
  
  ##############################################################################
  ### @fn   copyFromOrig()
  ### @desc Called when the user clicks the "copy from original" button.
  ##############################################################################
  def copyFromOrig(self):
    # Get the translated box's text cursor.
    # Using the cursor, the edit can be undone, which is preferable.
    cursor = self.ui.txtTranslated.textCursor()
    
    # Select the whole thing.
    cursor.select(QTextCursor.Document)
    
    # Replace it with the Original box.
    cursor.insertText(self.ui.txtOriginal.toPlainText())
    
    self.ui.txtTranslated.setTextCursor(cursor)
    
    self.ui.txtTranslated.setFocus()
  
  ##############################################################################
  ### @fn   surroundSelection()
  ### @desc Takes the selected text and surrounds it with the given text.
  ##############################################################################
  def surroundSelection(self, before, after):
    # Get the translated box's text cursor.
    # Using the cursor, the edit can be undone, which is preferable.
    cursor = self.ui.txtTranslated.textCursor()
    
    # Get the selected text.
    selection = cursor.selectedText()
    
    # Store our selection so we can maintain it.
    anchor = min(cursor.anchor(), cursor.position()) + len(before)
    length = len(selection)
    
    # Add the surrounding text.
    selection = before + selection + after
    
    # Replace it with the quoted text.
    cursor.insertText(selection)
    
    cursor.setPosition(anchor)
    cursor.setPosition(anchor + length, QTextCursor.KeepAnchor)
    
    # Update the text box.
    self.ui.txtTranslated.setTextCursor(cursor)
    
    self.ui.txtTranslated.setFocus()
  
  ##############################################################################
  ### @fn   replaceSelection()
  ### @desc Takes the selected text and replaces it with the given text.
  ##############################################################################
  def replaceSelection(self, replaceWith):
    # Get the translated box's text cursor.
    # Using the cursor, the edit can be undone, which is preferable.
    cursor = self.ui.txtTranslated.textCursor()
    
    # Insert the dash, replacing any selected text.
    cursor.insertText(replaceWith)
    
    # Update the text box.
    self.ui.txtTranslated.setTextCursor(cursor)
    
    self.ui.txtTranslated.setFocus()
  
  ##############################################################################
  ### @fn   expandAll()
  ### @desc ???
  ##############################################################################
  def expandAll(self):
    self.ui.treeDupes.expandAll()
    self.ui.treeSimilar.expandAll()
    self.ui.treeReferences.expandAll()
  
  ##############################################################################
  ### @fn   collapseAll()
  ### @desc ???
  ##############################################################################
  def collapseAll(self):
    self.ui.treeDupes.collapseAll()
    self.ui.treeSimilar.collapseAll()
    self.ui.treeReferences.collapseAll()
  
  ##############################################################################
  ### @fn   firstFile()
  ### @desc Selects the first file in the list. Triggered by Ctrl+PgUp.
  ##############################################################################
  def firstFile(self):
    self.ui.lstFiles.setCurrentRow(0)
  
  ##############################################################################
  ### @fn   lastFile()
  ### @desc Selects the last file in the list. Triggered by Ctrl+PgDn.
  ##############################################################################
  def lastFile(self):
    self.ui.lstFiles.setCurrentRow(self.ui.lstFiles.count() - 1)
  
  ##############################################################################
  ### @fn   prevFile()
  ### @desc Selects the previous file in the list. Triggered by PgUp.
  ##############################################################################
  def prevFile(self):
    current_row = self.ui.lstFiles.currentRow()
    if current_row > 0:
      self.ui.lstFiles.setCurrentRow(current_row - 1)
  
  ##############################################################################
  ### @fn   nextFile()
  ### @desc Selects the next file in the list. Triggered by PgDn.
  ##############################################################################
  def nextFile(self):
    current_row = self.ui.lstFiles.currentRow()
    if current_row < self.ui.lstFiles.count() - 1:
      self.ui.lstFiles.setCurrentRow(current_row + 1)
    
  ##############################################################################
  ### @fn   toggleHighlight()
  ### @desc Updates config + highlighter to reflect the change.
  ###       Triggered by Alt+H or the menu option.
  ##############################################################################
  def toggleHighlight(self):
    self.updateConfig()
    self.updateHighlight()
  
  ##############################################################################
  ### @fn   updateHighlight()
  ### @desc Updates the highlighter based on our setting.
  ###       Triggered by Alt+H or the menu option.
  ##############################################################################
  def updateHighlight(self):
    if common.editor_config.highlight_terms:
      self.ui.txtOriginal.load_keywords()
    else:
      self.ui.txtOriginal.clear_keywords()
  
  ##############################################################################
  ### @fn   updateTranslatedBoxCfg()
  ### @desc Updates the settings for the translated box based on our config.
  ##############################################################################
  def updateTranslatedBoxCfg(self):
    ##############################
    ### Spell-check settings
    ##############################
    if not common.editor_config.spell_check == self.ui.txtTranslated.spellcheck_enabled():
      if common.editor_config.spell_check:
        self.ui.txtTranslated.enable_spellcheck()
      else:
        self.ui.txtTranslated.disable_spellcheck()
    
    if not common.editor_config.spell_check_lang == self.ui.txtTranslated.get_language():
      self.ui.txtTranslated.set_language(common.editor_config.spell_check_lang)
    
    ##############################
    ### Text replacement
    ##############################
    self.ui.txtTranslated.enable_replacement = common.editor_config.text_repl
    if not common.editor_config.repl == self.ui.txtTranslated.replacements:
      self.ui.txtTranslated.replacements = common.editor_config.repl
    
    ##############################
    ### Other settings
    ##############################
    self.ui.txtTranslated.enable_smart_quotes = common.editor_config.smart_quotes
    self.ui.txtTranslated.enable_quick_clt = common.editor_config.quick_clt
  
  ##############################################################################
  ### @fn   showNodeInEditor()
  ### @desc Code duplication is for faggots.
  ##############################################################################
  def showNodeInEditor(self, node):
    if not node == None:
      directory = tree.tree_item_to_path(node)
      filename  = None
      
      # If we're at the leaf node, then pull back to the directory.
      if node.childCount() == 0:
        directory, filename = os.path.split(directory)
      
      if not dir_tools.normalize(directory) == dir_tools.normalize(self.directory):
        if not self.askUnsavedChanges():
          return
        self.loadDirectory(directory, selected_file = filename)
      else:
        self.setCurrentFile(filename)
  
  ##############################################################################
  ### @fn   showCurrentInExplorer()
  ### @desc omgwtfbbq
  ##############################################################################
  def showCurrentInExplorer(self):
    if not isinstance(self.script_pack[self.cur_script], ScriptFile):
      directory = self.script_pack.get_real_dir()
      directory = os.path.join(common.editor_config.data01_dir, directory)
      dir_tools.show_in_explorer(directory)
    else:
      dir_tools.show_in_explorer(self.script_pack[self.cur_script].filename)
  
  ##############################################################################
  ### @fn   showNodeInExplorer()
  ### @desc Code duplication is for faggots.
  ###       But comment duplication is pro.
  ##############################################################################
  def showNodeInExplorer(self, node):
    
    if not node == None:
      directory = tree.tree_item_to_path(node)
      filename = ""
      
      # If we're at the leaf node, then pull back to the directory.
      if node.childCount() == 0:
        directory, filename = os.path.split(directory)
      
      directory = dir_tools.expand_dir(directory)
      directory = os.path.join(common.editor_config.data01_dir, directory, filename)
      dir_tools.show_in_explorer(directory)
  
  ##############################################################################
  ### @fn   copyNodePath()
  ### @desc Copies the path of the given node to the clipboard.
  ##############################################################################
  def copyNodePath(self, node):
    if not node == None:
      text = "{%s}" % tree.tree_item_to_path(node)
      
      clipboard = QApplication.clipboard()
      clipboard.setText(text)
  
  ##############################################################################
  ### @fn   copyActivePath()
  ### @desc Copies the path of the active file to the clipboard.
  ##############################################################################
  def copyActivePath(self):
    filename = os.path.basename(self.script_pack[self.cur_script].filename)
    path = "{%s}" % os.path.join(self.script_pack.directory, filename)
    
    clipboard = QApplication.clipboard()
    clipboard.setText(path)
  
  ##############################################################################
  ### @fn   showAbout()
  ### @desc A simple About screen.
  ##############################################################################
  def showAbout(self):
    QtGui.QMessageBox.information(
      self,
      u"About",
      u"""
<b>The Super Duper Script Editor 2</b> v0.0.0.0<br/>
Copyright © 2012-2013 BlackDragonHunt, released under the GNU GPL (see file COPYING).<br/>
<br/>
Attributions:
<ol>
<li>Bitstring: Copyright (c) 2006-2012 Scott Griffiths; Licensed under the MIT License</li>
<li>Diff Match and Patch: Copyright 2006 Google Inc.; Licensed under the Apache License, Version 2.0</li>
<li>enum: Copyright © 2007–2009 Ben Finney &lt;ben+python@benfinney.id.au&gt;; Licensed under the GNU GPL, Version 3</li>
<li>GIM2PNG: Copyright (c) 2008; <a href="http://www.geocities.jp/junk2ool/">Website</a></li>
<li>GIMExport: Copyright © 2012 /a/nonymous scanlations; Used with permission.</li>
<li>mkisofs: Copyright (C) 1993-1997 Eric Youngdale (C); Copyright (C) 1997-2010 Joerg Schilling; Licensed under the GNU GPL</li>
<li>pngquant: Copyright (C) 1989, 1991 by Jef Poskanzer; Copyright (C) 1997, 2000, 2002 by Greg Roelofs, based on an idea by Stefan Schneider; Copyright 2009-2012 by Kornel Lesinski</li>
<li>ProjexUI: Copyright (c) 2011, Projex Software; Licensed under the LGPL</li>
<li>squish: Copyright (c) 2006 Simon Brown</li>
<li>Unique Postfix: Copyright (c) 2010 Denis Barmenkov; Licensed under the MIT License</li>
<li>Silk Icon Set: Copyright Mark James; Licensed under the Creative Commons Attribution 2.5 License; <a href="http://www.famfamfam.com/lab/icons/silk/">Website</a></li>
</ol>""",
      buttons = QtGui.QMessageBox.Ok,
      defaultButton = QtGui.QMessageBox.Ok
    )
  
  ##############################################################################
  ### @fn   calculateProgress()
  ### @desc Calculates.
  ##############################################################################
  def calculateProgress(self):
    calculate_progress(self)
  
  ##############################################################################
  ### @fn   checkForErrors()
  ### @desc Checks the translated script against an untranslated script
  ###       for any errors -- cases of the original, untranslated text differing.
  ##############################################################################
  def checkForErrors(self):
    
    base_dir = QtGui.QFileDialog.getExistingDirectory(self, caption = "Select the base directory", directory = common.editor_config.last_checked_with)
    if not base_dir == "":
      base_dir = os.path.abspath(base_dir)
    else:
      return
    
    common.editor_config.last_checked_with = base_dir
    common.editor_config.save_config()
    
    progress = QProgressDialog("Checking for script errors...", "Abort", 0, 72000, self)
    progress.setWindowTitle("Checking for Errors")
    progress.setWindowModality(Qt.Qt.WindowModal)
    progress.setValue(0)
    progress.setAutoClose(False)
    
    files = list(list_all_files(base_dir))
    progress.setMaximum(len(files))
    
    # For our dupe database, we need the relative file location, not absolute.
    dir_start = len(base_dir) + 1
    
    text_files = []
    
    for i, file in enumerate(files):
      if os.path.splitext(file)[1] == ".txt":
        text_files.append(file[dir_start:])
    
    progress.setValue(0)
    progress.setMaximum(len(text_files))
    errors = []
  
    for i, file in enumerate(text_files):
      if progress.wasCanceled():
        return
      
      if i % 100 == 0:
        progress.setValue(progress.value() + 100)
      
      base_file = os.path.join(base_dir, file)
      cur_file  = os.path.join(common.editor_config.data01_dir, file)
      
      base_script   = ScriptFile(base_file)
      
      if os.path.isfile(cur_file):
        cur_script  = ScriptFile(cur_file)
        
        if not base_script[common.editor_config.lang_orig].strip() == cur_script[common.editor_config.lang_orig].strip():
          errors.append(file)
      
      else:
        errors.append(file)
    
    progress.close()
    
    diffs = DiffsMenu()
    diffs.menu_name = "Script Errors"
    diffs.setWindowTitle(diffs.menu_name)
    diffs.set_folders(base_dir, common.editor_config.data01_dir, errors)
    diffs.exec_()
  
  ##############################################################################
  ### @fn   reloadDupes()
  ### @desc Requests a reload of the duplicate database.
  ##############################################################################
  def reloadDupes(self):
    dupe_db.load_csv(common.editor_config.dupes_csv)
    self.findInternalDupes()
    self.showDupes()
  
  ##############################################################################
  ### @fn   closeEvent()
  ### @desc Makes sure everything's saved before closing.
  ##############################################################################
  def closeEvent(self, event):
    if self.askUnsavedChanges():
      self.console.close()
      self.search_menu.close()
      self.open_menu.close()
      self.terminology_editor.close()
      self.progress_calc.close()
      
      # Record the last selected file before we fade out of existence.
      if not self.directory == "":
        self.recordSelectedFile()
      
      # Then make sure the config file is up-to-date.
      common.editor_config.save_config()
      script_analytics.SA.save()
      event.accept()
    else:
      event.ignore()

##### EOF #####
