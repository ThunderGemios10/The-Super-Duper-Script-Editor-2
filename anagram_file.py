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

from bitstring import BitStream, ConstBitStream
from enum import Enum
import os
import re
import shutil
import time

import common
from script_file import ScriptFile

BIN_DIR = os.path.join("all", "bin")

ANAGRAM_TYPE = Enum("Demo", "Full")

DEMO_FLAG      = ConstBitStream(hex = "0x2C01")
FULL_FLAG      = ConstBitStream(hex = "0xB400")

ANAGRAM_MAGIC  = ConstBitStream(hex = "0xD007")

LETTER_HIDDEN  = ConstBitStream(hex = "0x0000")
LETTER_VISIBLE = ConstBitStream(hex = "0x0100")

UNKNOWN_LENGTH = {
  ANAGRAM_TYPE.Demo : 8,
  ANAGRAM_TYPE.Full : 12,
}

ANAGRAM_DIR = "23_anagram.pak"

class AnagramFile():
  def __init__(self, filename = None):
    self.filename = filename
    
    self.type           = None
    self.solution_index = -1
    self.solution       = None
    self.extra_index    = -1
    self.extra          = None
    
    self.__unknown      = None
    
    self.easy           = None
    self.normal         = None
    self.hard           = None
    
    self.easy_orig      = None
    self.normal_orig    = None
    self.hard_orig      = None
    
    if not filename == None:
      self.load(filename)
  
  def load(self, filename):
    if not os.path.isfile(filename):
      self.filename = None
      return
    
    dat_file = ConstBitStream(filename = self.filename)
    
    type = dat_file.read(16)
    
    if not type == DEMO_FLAG and not type == FULL_FLAG:
      raise Exception("Invalid Anagram", "Invalid anagram type.")
    
    if type == DEMO_FLAG:
      type = ANAGRAM_TYPE.Demo
    else:
      type = ANAGRAM_TYPE.Full
    
    num_letters = dat_file.read('uintle:16')
    magic       = dat_file.read(16)
    
    if not magic == ANAGRAM_MAGIC:
      raise Exception("Invalid Anagram", "Invalid anagram magic.")
    
    solution_index = dat_file.read('uintle:16')
    extra_index    = dat_file.read('uintle:16')
    unknown        = dat_file.read(UNKNOWN_LENGTH[type] * 8)
    
    easy   = dat_file.read(num_letters * 2 * 8)
    normal = dat_file.read(num_letters * 2 * 8)
    hard   = None
    
    if type == ANAGRAM_TYPE.Full:
      hard = dat_file.read(num_letters * 2 * 8)
    
    easy_orig    = None
    normal_orig  = None
    hard_orig    = None
    
    if dat_file.pos >= dat_file.len:
      # If we don't have more data, then consider this untranslated.
      # Therefore, the data we collected becomes the data for the original anagram.
      easy_orig    = easy
      normal_orig  = normal
      hard_orig    = hard
      
      num_letters  = 0
      easy         = None
      normal       = None
      hard         = None
    else:
      # If we DO have more data, consider this translated and grab the
      # info about the untranslated anagram. This data is not used by the game,
      # only the translators.
      letters_orig = dat_file.read('uintle:16')
      easy_orig    = dat_file.read(letters_orig * 2 * 8)
      normal_orig  = dat_file.read(letters_orig * 2 * 8)
      if type == ANAGRAM_TYPE.Full:
        hard_orig  = dat_file.read(letters_orig * 2 * 8)
    
    ##########################################################
    ### Now convert all this into a useful format.
    ##########################################################
    base_dir = os.path.dirname(self.filename)
    
    self.type           = type
    self.solution_index = solution_index
    self.solution       = ScriptFile(os.path.join(base_dir, ANAGRAM_DIR, "%04d.txt" % self.solution_index))
    self.extra_index    = extra_index
    self.extra          = ScriptFile(os.path.join(base_dir, ANAGRAM_DIR, "%04d.txt" % self.extra_index))
    
    self.__unknown      = unknown
    
    self.easy           = self.parse_shown(easy)
    self.normal         = self.parse_shown(normal)
    self.hard           = self.parse_shown(hard)
    
    self.easy_orig      = self.parse_shown(easy_orig)
    self.normal_orig    = self.parse_shown(normal_orig)
    self.hard_orig      = self.parse_shown(hard_orig)
  
  ##############################################################################
  ### @fn    pack()
  ### @desc  Converts all the data into the anagram file format.
  ### @param for_game -- Whether to include the original, untranslated data.
  ###                    True = exclude untranslated, since we don't need it.
  ##############################################################################
  def pack(self, for_game = False):
    
    is_translated = False
    
    if not self.solution[common.editor_config.lang_trans] == "":
      is_translated = True
    
    # SAVE!
    output = BitStream()
    
    # Type flag
    if self.type == ANAGRAM_TYPE.Demo:
      output += DEMO_FLAG
    else:
      output += FULL_FLAG
    
    # Number of letters
    if is_translated:
      output += ConstBitStream(uintle = len(self.solution[common.editor_config.lang_trans]), length = 16)
    else:
      output += ConstBitStream(uintle = len(self.solution[common.editor_config.lang_orig]), length = 16)
    
    # Magic
    output += ANAGRAM_MAGIC
    
    # File indexes
    output += ConstBitStream(uintle = self.solution_index, length = 16)
    output += ConstBitStream(uintle = self.extra_index, length = 16)
    
    # Unknown
    output += self.__unknown
    
    # Shown/unshown
    if is_translated:
      num_letters = len(self.solution[common.editor_config.lang_trans])
      output += self.pack_shown(self.easy, num_letters)
      output += self.pack_shown(self.normal, num_letters)
      
      if self.type == ANAGRAM_TYPE.Full:
        output += self.pack_shown(self.hard, num_letters)
      
      if not for_game:
        num_letters = len(self.solution[common.editor_config.lang_orig])
        output += ConstBitStream(uintle = num_letters, length = 16)
    
    if not is_translated or not for_game:
      # This shows up either way.
      num_letters = len(self.solution[common.editor_config.lang_orig])
      output += self.pack_shown(self.easy_orig, num_letters)
      output += self.pack_shown(self.normal_orig, num_letters)
      
      if self.type == ANAGRAM_TYPE.Full:
        output += self.pack_shown(self.hard_orig, num_letters)
    
    return output
  
  def save(self, filename = None):
    if filename == None:
      if self.filename == None:
        return
      else:
        filename = self.filename
    
    output = self.pack(for_game = False)
    
    f = open(filename, "wb")
    output.tofile(f)
    f.close()
    
    dirname = os.path.dirname(filename)
    dirname = os.path.join(dirname, ANAGRAM_DIR)
    
    if not os.path.isdir(dirname):
      os.makedirs(dirname)
    
    self.solution.save(os.path.join(dirname, "%04d.txt" % self.solution_index))
    self.extra.save   (os.path.join(dirname, "%04d.txt" % self.extra_index))
  
  def backup(self):
    
    backup_loc = time.strftime("%Y.%m.%d_%H.%M.%S_ANAGRAM")
    
    dirname = common.editor_config.backup_dir
    dirname = os.path.join(dirname, backup_loc)
    
    # Make sure we have a place to put it.
    if not os.path.isdir(dirname):
      os.makedirs(dirname)
    
    basename = os.path.basename(self.filename)
    target = os.path.join(dirname, basename)
    
    shutil.copy(self.filename, target)
    
    # Now for the text files themselves.
    source_dir = os.path.dirname(self.filename)
    source_dir = os.path.join(source_dir, ANAGRAM_DIR)
    
    solution_source = os.path.join(source_dir, "%04d.txt" % self.solution_index)
    extra_source    = os.path.join(source_dir, "%04d.txt" % self.extra_index)
    
    target_dir = os.path.join(dirname, ANAGRAM_DIR)
    
    # Make sure we have a place to put it.
    if not os.path.isdir(target_dir):
      os.makedirs(target_dir)
    
    solution_target = os.path.join(target_dir, "%04d.txt" % self.solution_index)
    extra_target    = os.path.join(target_dir, "%04d.txt" % self.extra_index)
    
    shutil.copy(solution_source, solution_target)
    shutil.copy(extra_source, extra_target)
  
  def parse_shown(self, data):
    if data == None:
      return None
    
    # Two bytes per letter.
    num_letters = (data.len / 16)
    
    shown = []
    
    for i in range(1, num_letters + 1):
      letter = data.read(16)
      
      if letter == LETTER_VISIBLE:
        shown.append(i)
    
    return shown
  
  def pack_shown(self, shown, num_letters):
    data = BitStream()
    
    if shown == None:
      shown = []
    
    for i in range(1, num_letters + 1):
      if i in shown:
        data += LETTER_VISIBLE
      else:
        data += LETTER_HIDDEN
    
    return data
    
if __name__ == "__main__":

  from extract.pak import get_pak_files
  for x in range(12):
    data = ConstBitStream(filename = os.path.join(common.editor_config.data01_dir, BIN_DIR, "anagram2_level%02d.dat" % x))
    
    with open("wip/anagram%02d.txt" % x, "wb") as f:
      for name, table in get_pak_files(data):
        f.write(name[:4] + ": ")
        # for i in range(36):
          # print "%3d" % table.read("uintle:8"),
        for i in range(18):
          f.write("%6d " % table.read("intle:16"))
        f.write("\n")

### EOF ###