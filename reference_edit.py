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
from PyQt4.QtCore import QRect, pyqtSignal
from PyQt4.QtGui import QTextCursor

from reference_highlighter import ReferenceHighlighter
from make_unique import make_unique

import copy
import terminology
import time

class ReferenceEdit(QtGui.QTextEdit):
  ### SIGNALS ###
  refs_edited = pyqtSignal()
  
  def __init__(self, parent):
    super(ReferenceEdit, self).__init__(parent)
    self.setAcceptRichText(False)
    self.highlighter = ReferenceHighlighter(self.document())
    
    # Pull the highlighter's signal up a level so we can filter meaningful changes.
    self.highlighter.refs_edited.connect(self.__references_changed__)
    
    self.references = []
  
  def __references_changed__(self):
    old_refs = copy.deepcopy(self.references)
    
    self.references = []
    
    for ref_list in self.highlighter.references:
      for ref in ref_list:
        self.references.append(ref[0])
    
    self.references = make_unique(self.references)
    
    if not self.references == old_refs:
      self.refs_edited.emit()

### EOF ###