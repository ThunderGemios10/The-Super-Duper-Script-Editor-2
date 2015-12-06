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
from PyQt4.QtCore import QRect, QSignalMapper
from PyQt4.QtGui import QTextCursor, QApplication
from keyword_highlighter import KeywordHighlighter, Keyword

try:
  import cPickle as pickle
except:
  import pickle

import terminology
import time

class KeywordEdit(QtGui.QTextEdit):
  def __init__(self, parent):
    super(KeywordEdit, self).__init__(parent)
    self.setAcceptRichText(False)
    self.highlighter = KeywordHighlighter(self.document())
    self.setMouseTracking(True)
    
    self.last_edited = None
    
    #self.load_keywords()
  
  ##############################################################################
  ### @fn   mouseMoveEvent(event)
  ### @desc So we can catch ToolTip events.
  ##############################################################################
  def mouseMoveEvent(self, event):
    tooltip, rect = self.get_tooltip(event.pos())
    
    if not tooltip == "":
      QtGui.QToolTip.showText(event.globalPos(), tooltip, self, rect)
    else:
      QtGui.QToolTip.hideText()
    
    return super(KeywordEdit, self).mouseMoveEvent(event)
  
  ##############################################################################
  ### @fn   words_at_pos(line, pos)
  ### @desc Figure out what keywords are at the specific position.
  ##############################################################################
  def words_at_pos(self, line, pos):
    
    words = []
    
    for word in self.highlighter.matches[line]:
      if pos >= word[1] and pos < word[2]:
        words.append(word)
    
    return words
  
  ##############################################################################
  ### @fn   get_tooltip(pos)
  ### @desc Returns the tooltip and the boundaries for it given the cursor pos.
  ##############################################################################
  def get_tooltip(self, pos):
    cursor_pos = self.document().documentLayout().hitTest(QtCore.QPointF(pos), Qt.Qt.ExactHit)
    
    if cursor_pos == -1:
      return "", QRect()
    
    cursor   = QTextCursor(self.document())
    cursor.setPosition(cursor_pos)
    col      = cursor.positionInBlock()
    line     = cursor.blockNumber()
    
    tooltip = ""
    rect    = QRect()
    
    if line >= len(self.highlighter.matches):
      return "", QRect()
    
    match_start = 0
    match_len   = 0
    
    matches     = 0
    
    #for word in self.highlighter.matches[line]:
      #if col >= word[1] and col < word[2]:
    for word in self.words_at_pos(line, col):
      keyword     = word[0]
      
      # Go for the smallest region possible so we can update
      # as soon as the mouse falls out of range of one of the words.
      if word[1] > match_start:
        match_start = word[1]
      
      if word[2] - word[1] < match_len:
        match_len = word[2] - word[1]
      
      if matches > 0:
        tooltip += u"\n"
      
      if not keyword.section == "":
        tooltip += u"【%s】 " % keyword.section
      
      tooltip += u"%s ― %s" % (keyword.word, keyword.meaning)
      
      matches += 1
    
    # Highlight our word, so we can get the rect.
    cursor.movePosition(QTextCursor.Start)
    
    for i in range(line):
      cursor.movePosition(QTextCursor.NextBlock)
    
    for i in range(match_start):
      cursor.movePosition(QTextCursor.NextCharacter)
    
    for i in range(match_len):
      cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
    
    rect = self.cursorRect(cursor)
    
    return tooltip, rect
  
  ##############################################################################
  ### @fn   contextMenuEvent(event)
  ### @desc Generates a context menu depending on what keywords are under the cursor.
  ##############################################################################
  def contextMenuEvent(self, event):
    menu     = QtGui.QMenu()
    last_pos = event.pos()
    cursor   = self.cursorForPosition(last_pos)
    pos      = cursor.positionInBlock()
    line     = cursor.blockNumber()
    
    keywords = self.words_at_pos(line, pos)
    
    if len(keywords) > 0:
      keyword_mapper = QSignalMapper(self)
      
      actions = []
      
      for keyword in keywords:
        
        action_text = "Copy \"%s\"" % keyword[0].meaning
        actions.append(QtGui.QAction(action_text, None))
        
        # We can only send strings with the signal mapper, so pickle our data.
        data = pickle.dumps(keyword[0])
        data = QtCore.QString.fromAscii(data)
        
        self.connect(actions[-1], QtCore.SIGNAL("triggered()"), keyword_mapper, QtCore.SLOT("map()"))
        keyword_mapper.setMapping(actions[-1], data)
      
      self.connect(keyword_mapper, QtCore.SIGNAL("mapped(QString)"), self.copy_keyword)
      menu.addActions(actions)
      menu.addSeparator()
    
    default_menu = self.createStandardContextMenu()
    menu.addActions(default_menu.actions())
    
    menu.exec_(event.globalPos())
  
  ##############################################################################
  ### @fn   copy_keyword(data)
  ### @desc Sends the "meaning" portion of a keyword to the clipboard.
  ##############################################################################
  def copy_keyword(self, data):
    # Since Qt's Signal Mapper will only accept a QString, we have to convert it
    # to a Python string in such a way that it won't try to actually encode/decode
    # any of the data, because nothing but the container changed when it turned
    # into a QString.
    keyword = pickle.loads(data.toAscii().data())    
    
    clipboard = QApplication.clipboard()
    clipboard.setText(keyword.meaning)
  
  ##############################################################################
  ### @fn   load_keywords()
  ### @desc Checks to see if the terminology file has been changed since
  ###       the last load, and if not, loads them.
  ##############################################################################
  def load_keywords(self):
    
    csv_edited = terminology.last_edited()
    
    if self.last_edited == csv_edited:
      return
    else:
      self.last_edited = csv_edited
    
    self.highlighter.clear_keywords()
    rows = terminology.load_csv()
    
    for row in rows:
      section = row['Section'].decode("UTF-8")
      word    = row['Word'].decode("UTF-8")
      meaning = row['Meaning'].decode("UTF-8")
      
      term = terminology.Term(word, meaning, section)
      self.highlighter.add_keyword(term)
    
    self.highlighter.rehighlight()
  
  ##############################################################################
  ### @fn   clear_keywords()
  ### @desc Bye bye.
  ##############################################################################
  def clear_keywords(self):
    self.highlighter.clear_keywords()
    self.highlighter.rehighlight()
    
    # So we force a reload.
    self.last_edited = -1

### EOF ###