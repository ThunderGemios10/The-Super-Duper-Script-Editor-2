################################################################################
### Copyright © 2013 BlackDragonHunt
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

from PyQt4 import Qt, QtGui
from PyQt4.QtGui import QTextCursor
from spellcheck_edit import SpellCheckEdit

import re

################################################################################
### CONSTANTS
################################################################################
APOSTROPHE  = u"'"
QUOTE       = u"\""
LEFT_APOST  = u"‘"
RIGHT_APOST = u"’"
LEFT_QUOTE  = u"“"
RIGHT_QUOTE = u"”"

DEFAULT_REPL = [(u"--", u"—"),
                (u"—-", u"–"),
               ]

CLT_BEGIN     = u"<"
CLT_END       = u">"
RE_QUICK_CLT  = re.compile(ur"\<(?P<CLT_INDEX>\d+)?\>", re.UNICODE)
RE_FULL_CLT   = re.compile(ur"\<CLT(\s+(?P<CLT_INDEX>\d+))?\>", re.UNICODE)

################################################################################
### SmartTextEdit Class
################################################################################
class SmartTextEdit(SpellCheckEdit):
  def __init__(self, parent):
    super(SmartTextEdit, self).__init__(parent)
    
    self.changing_text = False
    self.textChanged.connect(self.changed_text)
    
    self.enable_replacements = True
    self.enable_smart_quotes = True
    self.enable_quick_clt = True
    self.replacements = DEFAULT_REPL
  
  def changed_text(self):
    # So we don't get caught in infinite death if we have a recursive replacement
    if self.changing_text:
      return
    
    self.changing_text = True
    
    cursor = self.textCursor()
    
    if self.enable_smart_quotes:
      cursor = self.smart_quotes(cursor)
    
    if self.enable_quick_clt:
      cursor = self.quick_clt(cursor)
    
    if self.enable_replacements:
      cursor = self.handle_replacements(cursor)
    
    self.setTextCursor(cursor)
    
    self.changing_text = False
  
  def smart_quotes(self, cursor):
    # Nothing to do at the start of a block.
    if cursor.atBlockStart():
      return cursor
    
    pos  = cursor.positionInBlock()
    text = unicode(cursor.block().text().toUtf8(), "UTF-8")
    
    char = text[pos - 1 : pos]
    if not char in [APOSTROPHE, QUOTE]:
      return cursor
    
    repl_with = None
    
    if pos == 1:
      prev_char = None
    else:
      prev_char = text[pos - 2 : pos - 1]
    
    # It's a left quote/apost if it comes after a space, a tab,
    # a left-bracket-type thing or the left of the opposite type of quote,
    # or the right of same type of quote.
    if prev_char in [None, u" ", u"\t", u"(", u"[", u"{", u"<", u">", u"\uFFFC", LEFT_APOST if char == QUOTE else LEFT_QUOTE, RIGHT_QUOTE if char == QUOTE else RIGHT_APOST]:
      repl_with = LEFT_QUOTE if char == QUOTE else LEFT_APOST
    else:
      repl_with = RIGHT_QUOTE if char == QUOTE else RIGHT_APOST
    
    cursor.setPosition(cursor.position())
    cursor.setPosition(cursor.position() - 1, QTextCursor.KeepAnchor)
    cursor.insertText(repl_with)
    
    return cursor
  
  def quick_clt(self, cursor):
    # Nothing to do at the start of a block.
    if cursor.atBlockStart():
      return cursor
    
    pos  = cursor.position()
    text = unicode(cursor.document().toPlainText().toUtf8(), "UTF-8")
    
    char = text[pos - 1 : pos]
    if not char == CLT_END:
      return cursor
    
    # Find the first < *before* this >
    clt_begin = text.rfind(CLT_BEGIN, 0, pos)
    clt_end   = pos
    
    # Get the requested CLT
    match = RE_QUICK_CLT.match(text, clt_begin, clt_end)
    
    if not match or not (match.start() == clt_begin and match.end() == clt_end):
      return cursor
    
    clt = int(match.groupdict(default = "0")["CLT_INDEX"])
    
    # Now look for an existing, open CLT before this.
    prev_clt_begin  = text.rfind(CLT_BEGIN, 0, clt_begin)
    prev_clt        = 0
    
    match = RE_FULL_CLT.match(text, prev_clt_begin, clt_begin)
    if match:
      prev_clt = match.group("CLT_INDEX")
      
      if prev_clt == None:
        prev_clt = 0
      else:
        prev_clt = int(prev_clt)
    
    left  = ""
    right = ""
    
    if not prev_clt == clt:
      if not prev_clt == 0:
        left  = "<CLT>"
        # right = "<CLT %02d>" % prev_clt
      # else:
        # right = "<CLT>"
      
      if not clt == 0:
        left  = left + "<CLT %02d>" % clt
        # right = "<CLT>" + right
    
    cursor.setPosition(cursor.position())
    cursor.setPosition(cursor.position() - (clt_end - clt_begin), QTextCursor.KeepAnchor)
    cursor.insertText(left + right)
    
    cursor.setPosition(clt_begin + len(left))
    
    return cursor
  
  def handle_replacements(self, cursor):
    # Nothing to do at the start of a block.
    if cursor.atBlockStart():
      return cursor
    
    pos  = cursor.positionInBlock()
    text = unicode(cursor.block().text().toUtf8(), "UTF-8")
    
    for (repl, repl_with) in self.replacements:
      if pos < len(repl):
        continue
      
      if text[pos - len(repl) : pos] == repl:
        cursor.setPosition(cursor.position())
        cursor.setPosition(cursor.position() - len(repl), QTextCursor.KeepAnchor)
        cursor.insertText(repl_with)
        break
    
    return cursor

### EOF ###