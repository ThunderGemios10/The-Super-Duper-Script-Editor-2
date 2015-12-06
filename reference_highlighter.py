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
from PyQt4.QtCore import pyqtSignal

import copy
import re

import common

RE_REFERENCE = re.compile(ur"\{([^\{\}]+?\.txt)\}", re.UNICODE | re.S | re.DOTALL)

class ReferenceHighlighter(QtGui.QSyntaxHighlighter):
  ### SIGNALS ###
  refs_edited = pyqtSignal()
  
  def __init__(self, parent = None):
    super(ReferenceHighlighter, self).__init__(parent)
    
    self.format = QTextCharFormat()
    self.format.setForeground(QColor(0, 0, 255))
    
    self.references = []
  
  def highlightBlock(self, text):
    
    # If there is no previous state, then it's -1, which makes the first line 0.
    # And every line after that increases as expected.
    line = self.previousBlockState() + 1
    self.setCurrentBlockState(line)
    
    old_refs = copy.deepcopy(self.references)
    
    # Make sure we aren't too long.
    if len(self.references) > self.parent().blockCount():
      self.references = self.references[:self.parent().blockCount()]
    
    # Make sure our matches list is long enough to hold this line.
    for i in range(len(self.references), line + 1):
      self.references.append([])
    
    if len(self.references) == 0:
      return
    
    self.references[line] = []
    
    text = common.qt_to_unicode(text).lower()
    
    matches = RE_REFERENCE.finditer(text)
    
    for match in matches:
      self.setFormat(match.start(), match.end() - match.start(), self.format)
      self.references[line].append((match.group(1), match.start() + 1))
    
    if not old_refs == self.references:
      self.refs_edited.emit()

### EOF ###