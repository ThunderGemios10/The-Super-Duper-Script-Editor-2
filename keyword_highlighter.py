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
from PyQt4.QtGui import QTextCharFormat, QColor

import re
import common

# lol
from terminology import Term as Keyword

def allindices(string, sub, listindex=[], offset=0):
  i = string.find(sub, offset)
  while i >= 0:
    listindex.append(i)
    i = string.find(sub, i + 1)
  return listindex

class KeywordHighlighter(QtGui.QSyntaxHighlighter):
  def __init__(self, parent = None):
    super(KeywordHighlighter, self).__init__(parent)
    
    self.format = QTextCharFormat()
    self.format.setForeground(QColor(255, 0, 0))
    
    self.keywords = []
    self.matches  = []
    
    self.re_flags = re.IGNORECASE | re.UNICODE
  
  def highlightBlock(self, text):
    
    # If there is no previous state, then it's -1, which makes the first line 0.
    # And every line after that increases as expected.
    line = self.previousBlockState() + 1
    self.setCurrentBlockState(line)
    
    # Make sure we aren't too long.
    if len(self.matches) > self.parent().blockCount():
      self.matches = self.matches[:self.parent().blockCount()]
      
    # Make sure our matches list is long enough to hold this line.
    for i in range(len(self.matches), line + 1):
      self.matches.append([])
    
    if len(self.keywords) == 0:
      return
    
    self.matches[line] = []
    
    text = common.qt_to_unicode(text)
    
    for keyword in self.keywords:
      matches = keyword.compiled.finditer(text)
      
      for match in matches:
        self.setFormat(match.start(), match.end() - match.start(), self.format)
        
        keyword_match = Keyword()
        keyword_match.word = match.group()
        keyword_match.meaning = keyword.meaning
        keyword_match.section = keyword.section
        
        self.matches[line].append((keyword_match, match.start(), match.end()))
  
  def add_keyword(self, word):
    word.compiled = re.compile(word.word, self.re_flags)
    self.keywords.append(word)
  
  def add_keywords(self, words):
    for word in words:
      self.add_keyword(word)
  
  def set_keyword(self, word):
    self.clear_keywords()
    self.add_keyword(word)
  
  def set_keywords(self, words):
    self.clear_keywords()
    self.add_keywords(words)
  
  def clear_keywords(self):
    self.keywords = []
    #self.rehighlight()

### EOF ###