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

import bitstring
from bitstring import BitStream, ConstBitStream

import logging
import os

import common

from script_file import ScriptFile
# from anagram_file import AnagramFile

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

# UTF-16 byte-order-marker, since we store the text in UTF-8.
SCRIPT_BOM  = u"\uFEFF"
SCRIPT_NULL = u"\u0000"

SCRIPT_NONSTOP = [
  "e01_202_001.lin",
  "e01_204_001.lin",
  "e01_208_001.lin",
  "e01_210_001.lin",
  "e01_212_001.lin",
  "e01_216_001.lin",
  "e01_222_001.lin",
  "e01_224_001.lin",
  "e01_228_001.lin",
  "e01_206_001.lin",
  "e01_214_001.lin",
  "e01_226_001.lin",
]

def pack_file(filename):

  basename = os.path.basename(filename)
  basename, ext = os.path.splitext(basename)
  
  # Special handling for certain data types.
  if ext == ".txt":
    data = pack_txt(filename)
  
  # anagram_81.dat is not a valid anagram file. <_>
  # elif basename[:8] == "anagram_" and ext == ".dat" and not basename == "anagram_81":
    # anagram = AnagramFile(filename)
    # data    = anagram.pack(for_game = True)
  
  else:
    with open(filename, "rb") as f:
      data = BitStream(bytes = f.read())
  
  return data

def pack_txt(filename):
  
  if os.path.basename(os.path.dirname(filename)) in SCRIPT_NONSTOP:
    is_nonstop = True
  else:
    is_nonstop = False

  script = ScriptFile(filename)
  text = script[common.editor_config.lang_trans]
  if not text:
    text = script[common.editor_config.lang_orig]
  
  # Nonstop Debate lines need an extra newline at the end
  # so they show up in the backlog properly.
  if is_nonstop and not text[-1] == u"\n":
    text += u"\n"
  
  text = SCRIPT_BOM + text + SCRIPT_NULL
  text = BitStream(bytes = text.encode("UTF-16LE"))
  
  return text

if __name__ == "__main__":
  pass

### EOF ###