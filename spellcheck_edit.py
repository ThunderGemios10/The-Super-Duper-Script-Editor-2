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

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QTextCursor
from PyQt4.QtCore import QSignalMapper
from spellcheck_highlighter import SpellCheckHighlighter

try:
  import cPickle as pickle
except:
  import pickle
  
import common

MAX_SUGGESTIONS = 6

class SpellCheckEdit(QtGui.QTextEdit):
  def __init__(self, parent):
    super(SpellCheckEdit, self).__init__(parent)
    self.setAcceptRichText(False)
    self.highlighter = SpellCheckHighlighter(self.document())
  
  def set_language(self, lang):
    self.highlighter.set_language(lang)
  
  def get_language(self):
    return self.highlighter.get_language()
  
  def spellcheck_enabled(self):
    return self.highlighter.document() == self.document()
  
  def enable_spellcheck(self):
    self.highlighter.setDocument(self.document())
  
  def disable_spellcheck(self):
    self.highlighter.setDocument(None)
  
  ##############################################################################
  ### @fn   error_at_pos(line, pos)
  ### @desc Figure out what error is at the specific position.
  ##############################################################################
  def error_at_pos(self, line, pos):
    
    for word in self.highlighter.errors[line]:
      if pos >= word[1] and pos < word[1] + len(word[0]):
        return word
    
    return None
  
  ##############################################################################
  ### @fn   contextMenuEvent(event)
  ### @desc Generates a context menu depending on what error is under the cursor.
  ##############################################################################
  def contextMenuEvent(self, event):
    menu     = QtGui.QMenu()
    last_pos = event.pos()
    cursor   = self.cursorForPosition(last_pos)
    pos      = cursor.positionInBlock()
    line     = cursor.blockNumber()
    
    word = self.error_at_pos(line, pos)
    
    if not word == None:
      suggestions = self.highlighter.checker.suggest(word[0])
      
      if len(suggestions) > 0:
        suggestion_mapper = QSignalMapper(self)
        
        actions = []
        
        # Generate our suggestions, packing all the data we need to make the replacement.
        for i, suggestion in enumerate(suggestions):
          if i == MAX_SUGGESTIONS:
            break
          
          actions.append(QtGui.QAction(suggestion, None))
          
          # We can only send strings with the signal mapper, so pickle our data.
          data = pickle.dumps((word[0], line, word[1], suggestion))
          data = QtCore.QString.fromAscii(data)
          
          self.connect(actions[-1], QtCore.SIGNAL("triggered()"), suggestion_mapper, QtCore.SLOT("map()"))
          suggestion_mapper.setMapping(actions[-1], data)
        
        self.connect(suggestion_mapper, QtCore.SIGNAL("mapped(QString)"), self.__replace)
        menu.addActions(actions)
      else:
        action = QtGui.QAction("(No spelling suggestions)", None)
        action.setDisabled(True)
        menu.addAction(action)
        
      menu.addSeparator()
      
      add_mapper    = QSignalMapper(self)
      ignore_mapper = QSignalMapper(self)
      add_action = QtGui.QAction("Add to Dictionary", None)
      ignore_action = QtGui.QAction("Ignore All", None)
      
      self.connect(add_action, QtCore.SIGNAL("triggered()"), add_mapper, QtCore.SLOT("map()"))
      add_mapper.setMapping(add_action, word[0])
      self.connect(add_mapper, QtCore.SIGNAL("mapped(QString)"), self.__add)
      
      self.connect(ignore_action, QtCore.SIGNAL("triggered()"), ignore_mapper, QtCore.SLOT("map()"))
      ignore_mapper.setMapping(ignore_action, word[0])
      self.connect(ignore_mapper, QtCore.SIGNAL("mapped(QString)"), self.__ignore)
      
      menu.addAction(add_action)
      menu.addAction(ignore_action)
      menu.addSeparator()
    
    default_menu = self.createStandardContextMenu()
    menu.addActions(default_menu.actions())
    
    menu.exec_(event.globalPos())
  
  ##############################################################################
  ### @fn   add(word)
  ### @desc Adds the given word to the dictionary.
  ##############################################################################
  def __add(self, word):
    self.highlighter.add(common.qt_to_unicode(word))
  
  ##############################################################################
  ### @fn   ignore(word)
  ### @desc Tells the dictionary to ignore the given error.
  ##############################################################################
  def __ignore(self, word):
    self.highlighter.ignore(common.qt_to_unicode(word))
  
  ##############################################################################
  ### @fn   replace(data)
  ### @desc Replaces the word under the cursor with the word given.
  ##############################################################################
  def __replace(self, data):
    # Since Qt's Signal Mapper will only accept a QString, we have to convert it
    # to a Python string in such a way that it won't try to actually encode/decode
    # any of the data, because nothing but the container changed when it turned
    # into a QString.
    word, line, pos, repl_with = pickle.loads(data.toAscii().data())
    
    cursor = self.textCursor()
    
    cursor.movePosition(QTextCursor.Start)
    
    for i in range(line):
      cursor.movePosition(QTextCursor.NextBlock)
    
    for i in range(pos):
      cursor.movePosition(QTextCursor.NextCharacter)
    
    for i in range(len(word)):
      cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
    
    cursor.insertText(repl_with)
    
    self.setTextCursor(cursor)

### EOF ###