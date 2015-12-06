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

import os
import re

from collections import defaultdict

try:
  import xml.etree.cElementTree as ET
except:
  import xml.etree.ElementTree as ET

from text_files import load_text
from scene_info import SceneInfo

# Some regexes for our enjoyment.
LINE_BREAKS = re.compile(ur"\r\n?", re.UNICODE | re.DOTALL)
TAG_KILLER  = re.compile(ur"\<CLT\>|\<CLT (?P<CLT_INDEX>\d+)\>|<DIG.*?>", re.UNICODE | re.DOTALL)

################################################################################
### CONSTANTS
################################################################################
LINE_TAG      = u"line"
TEXT_TAG      = u"text"
LANG_ATTR     = u"lang"
COMMENT_TAG   = u"comment"

DEFAULT_LANG  = u"ja"

INDENT        = u"  "

################################################################################
### HELPER FUNCTIONS
################################################################################
# Modified from http://stackoverflow.com/a/12940014
def indent_xml(elem, level = 0, more_sibs = False):
  i = "\n"
  if level:
    i += (level - 1) * INDENT
  
  num_kids = len(elem)
  if num_kids:
    if not elem.text or not elem.text.strip():
      elem.text = i + INDENT
      if level:
        elem.text += INDENT
    
    for x, kid in enumerate(elem):
      indent_xml(kid, level + 1, x < num_kids - 1)
    
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
      if more_sibs:
        elem.tail += INDENT
  
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i
      if more_sibs:
        elem.tail += INDENT
  
class NoTags:
  def __init__(self, parent):
    self.parent = parent

  def __getitem__(self, lang):
    return TAG_KILLER.sub(u"", self.parent[lang])

################################################################################
### ScriptFile CLASS
################################################################################
class ScriptFile(object):
  
  def __init__(self, filename = None, scene_info = None):
    self.text     = defaultdict(unicode)
    self.notags   = NoTags(self)
    self.comments = ""
    self.filename = None
    
    if not filename == None:
      self.open(filename)
    
      if scene_info == None:
        # Squeeze the file ID out of the filename.
        scene_info = SceneInfo(file_id = int(os.path.splitext(os.path.basename(filename))[0]))
    
    self.scene_info = scene_info
      
  def __getitem__(self, lang):
    return self.text[lang]
  
  def __setitem__(self, lang, text):
    self.text[lang] = text
  
  # def __get_notags__(self):
    # __notags = defaultdict(unicode)
    # for lang in self.text.keys():
      # __notags[lang] = TAG_KILLER.sub(u"", self.text[lang])
    # return __notags
  
  # notags = property(fget = __get_notags__)
  
  def open(self, filename):
    
    try:
      tree = ET.parse(filename)
      root = tree.getroot()
    
    except ET.ParseError:
      # If it fails to parse as XML, assume it's the default format from the game.
      text = load_text(filename).strip("\0")
      text = LINE_BREAKS.sub("\n", text)
      
      root = ET.Element(LINE_TAG)
      
      line = ET.SubElement(root, TEXT_TAG)
      line.set(LANG_ATTR, DEFAULT_LANG)
      line.text = text
      
    except:
      raise
    
    self.text     = defaultdict(unicode)
    self.comments = u""
    
    for child in root:
      if child.tag == TEXT_TAG:
        lang = child.get(LANG_ATTR, DEFAULT_LANG)
        if child.text:
          self.text[lang] = child.text
        else:
          self.text[lang] = u""
      
      elif child.tag == COMMENT_TAG:
        if child.text:
          self.comments = child.text
        else:
          self.comments = u""
    
    self.filename = filename
  
  def save(self, filename = None):
    
    if filename == None:
      if self.filename == None:
        raise ValueError("No filename provided for save operation.")
      else:
        filename = self.filename
    
    root = ET.Element(LINE_TAG)
    
    for lang in sorted(self.text.keys()):
      line = ET.SubElement(root, TEXT_TAG)
      line.set(LANG_ATTR, lang)
      line.text = self.text[lang]
      # line.tail = u"\n"
    
    if self.comments:
      comment = ET.SubElement(root, COMMENT_TAG)
      comment.text = self.comments
      # comment.tail = u"\n"
    
    indent_xml(root)
    tree = ET.ElementTree(root)
    tree.write(filename, encoding = "UTF-8", xml_declaration = False)

### EOF ###