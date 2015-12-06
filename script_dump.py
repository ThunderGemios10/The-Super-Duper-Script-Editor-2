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

import common

from object_labels import get_map_name, get_char_name
from mtb import MTBParser
from nonstop import NonstopParser
from script_pack import ScriptPack
from voice import get_voice_file

def script_to_text(dir, translated = True, strip_clt = False, only_voiced = False, line_numbers = True):
  script_pack = ScriptPack()
  
  if dir[:7] == "nonstop":
    parser = NonstopParser()
    parser.load(dir)
    script_pack = parser.script_pack
  
  elif dir[:8] == "hs_mtb_s":
    parser = MTBParser()
    parser.load(dir)
    script_pack = parser.script_pack
  
  elif dir[:7] == "anagram":
    return u""
  
  else:
    script_pack.load_dir(dir, common.editor_config.data01_dir)
  
  # pack = ScriptPack(directory = dir, umdimage = "X:/Danganronpa/Demo_FINAL/umdimage/")
  
  output = []
  
  if len(script_pack) > 0:
  
    output.append("==================================================\n=== %s" % dir)
    room = get_map_name(script_pack[0].scene_info.room)
    if not room == None:
      output.append("\n=== Room: %s" % room)
    output.append("\n==================================================\n\n")
    
    for script in script_pack:
      voice = get_voice_file(script.scene_info.voice)
      if voice == None and only_voiced:
        continue
      
      if script.scene_info.special in [common.SCENE_SPECIAL.checkobj, common.SCENE_SPECIAL.checkchar, common.SCENE_SPECIAL.option, common.SCENE_SPECIAL.showopt]:
        output.append("********************\n\n")
      
      if line_numbers:
        output.append("[%04d.txt]" % script.scene_info.file_id)
        output.append("\n")
      
      char_name = get_char_name(script.scene_info.speaker)
      output.append("[%s]\n" % (char_name if char_name else "N/A"))
      
      if not voice == None:
        # output.append("  [Voice: %04d.at3, %s]\n" % (voice, common.CHAR_IDS[script.scene_info.voice.char_id] if script.scene_info.voice.char_id in common.CHAR_IDS else "N/A"))
        output.append("[Voice: %04d.at3" % (voice))
        if script.scene_info.voice.chapter == 0x63:
          output.append(" (Generic)")
        output.append("]\n")
      # output.append("\n")
      
      line = ""
      if translated and script[common.editor_config.lang_trans]:
        if strip_clt:
          line = script.notags[common.editor_config.lang_trans]
        else:
          line = script[common.editor_config.lang_trans]
      
      else:
        if strip_clt:
          line = script.notags[common.editor_config.lang_orig]
        else:
          line = script[common.editor_config.lang_orig]
      
      output.append("  %s" % line.strip().replace("\n", "\n  "))
      output.append("\n\n")
  
  return u''.join(output)

def main():
  wrd_lists = [
    # ("wip/wrd-prologue.txt",  "wip/script-prologue.txt"),
    # ("wip/wrd-ch1-1.txt",     "wip/script-ch1-1.txt"),
    # ("wip/wrd-ch1-2.txt",     "wip/script-ch1-2.txt"),
    ("wip/wrd-ch1-3.txt",     "wip/script-ch1-3.txt"),
  ]
  
  for source, output in wrd_lists:
    
    dirs = []
    with open(source, "rb") as f:
      dirs = [dir for dir in f.read().split("\n") if not dir[:7] == "anagram"]
    
    with open(output, "wb") as f:
      for dir in dirs:
        script = script_to_text(dir)
        f.write(script.encode("UTF-8"))

if __name__ == "__main__":
  main()

### EOF ###