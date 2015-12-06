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

from bitstring import ConstBitStream
import logging
import os

import common
  
from extract.pak import get_pak_files
from script_pack import ScriptPack
from sprite import SpriteId, SPRITE_TYPE
from voice import VoiceId

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

BIN_DIR = os.path.join("all", "bin")

MTB_DIR = {
  # "hs_mtb_s01.pak":   "mtb_s01.pak",
  # "hs_mtb_s02.pak":   "mtb_s02.pak",
  # "hs_mtb_s03.pak":   "mtb_s03.pak",
  # "hs_mtb_s04.pak":   "mtb_s04.pak",
  # "hs_mtb_s05.pak":   "mtb_s05.pak",
  # "hs_mtb_s06.pak":   "mtb_s06.pak",
  # "hs_mtb_s07.pak":   "mtb_s07.pak",
  # "hs_mtb_s08.pak":   "mtb_s08.pak",
  # "hs_mtb_s09.pak":   "mtb_s09.pak",
  # "hs_mtb_s10.pak":   "mtb_s10.pak",
  # "hs_mtb_s11.pak":   "mtb_s11.pak",
  # "hs_mtb_s21.pak":   "mtb_s21.pak",
  # "hs_mtb_s22.pak":   "mtb_s22.pak",
  # "hs_mtb_s23.pak":   "mtb_s23.pak",
  # "hs_mtb_s24.pak":   "mtb_s24.pak",
  # "hs_mtb_s25.pak":   "mtb_s25.pak",
  # "hs_mtb_s26.pak":   "mtb_s26.pak",
  # "hs_mtb_s27.pak":   "mtb_s27.pak",
  # "hs_mtb_s28.pak":   "mtb_s28.pak",
  # "hs_mtb_s29.pak":   "mtb_s29.pak",
  # "hs_mtb_s30.pak":   "mtb_s30.pak",
  # "hs_mtb_s31.pak":   "mtb_s31.pak",
  # "hs_mtb_s32.pak":   "mtb_s32.pak",
  # "hs_mtb_s33.pak":   "mtb_s33.pak",
  # "hs_mtb_s34.pak":   "mtb_s34.pak",
  # "hs_mtb_s35.pak":   "mtb_s35.pak",
  # "hs_mtb_s36.pak":   "mtb_s36.pak",
  # "hs_mtb_s37.pak":   "mtb_s37.pak",
  # "hs_mtb_s38.pak":   "mtb_s38.pak",
  # "hs_mtb_s39.pak":   "mtb_s39.pak",
  # "hs_mtb_s40.pak":   "mtb_s40.pak",
  "dr2_mtb2_s01.pak": "mtb2_s01.pak",
  "dr2_mtb2_s02.pak": "mtb2_s02.pak",
  "dr2_mtb2_s03.pak": "mtb2_s03.pak",
  "dr2_mtb2_s04.pak": "mtb2_s04.pak",
  "dr2_mtb2_s05.pak": "mtb2_s05.pak",
  "dr2_mtb2_s06.pak": "mtb2_s06.pak",
  "dr2_mtb2_s07.pak": "mtb2_s07.pak",
  "dr2_mtb2_s08.pak": "mtb2_s08.pak",
  "dr2_mtb2_s09.pak": "mtb2_s09.pak",
  "dr2_mtb2_s10.pak": "mtb2_s10.pak",
}

class MTBParser():
  def __init__(self):
    self.script_pack = ScriptPack()
    self.filename = ""
  
  def load(self, filename):
    filename = filename.lower()
    
    if not filename in MTB_DIR:
      _LOGGER.error("Invalid MTB file: %s" % filename)
      return
    
    self.filename = filename
    
    script_dir = MTB_DIR[filename]
    self.script_pack = ScriptPack(script_dir, common.editor_config.data01_dir)
    
    # --- MTB FORMAT ---
    # A nested pak of our standard game paks.
    # Each file comes with three paks (four in the first game).
    # The first pak has a single file with information about the MTB as a whole.
    # The second one contains information about individual lines.
    # The third one, I dunno. Always seems to have 120 items?
    
    mtb = ConstBitStream(filename = os.path.join(common.editor_config.data01_dir, BIN_DIR, self.filename))
    paks = [data for name, data in get_pak_files(mtb)]
    
    mtb_data  = paks[0]
    line_data = paks[1]
    
    for name, data in get_pak_files(mtb_data):
      mtb_index   = data.read("uintle:16")
      sprite_char = data.read("uintle:16")
      voice_char  = data.read("uintle:16")
      sprite_id   = data.read("uintle:16")
    
    sprite = SpriteId(SPRITE_TYPE.stand, sprite_char, sprite_id)
    
    for name, data in get_pak_files(line_data):
      file_id  = data.read("uintle:16")
      voice_ch = data.read("uintle:16")
      voice_id = data.read("uintle:16")
      
      voice = VoiceId(voice_char, voice_ch, voice_id)
      
      self.script_pack[file_id].scene_info.sprite = sprite
      self.script_pack[file_id].scene_info.voice  = voice
      # self.script_pack[file_id].scene_info.mode   = common.SCENE_MODES.mtb

if __name__ == "__main__":
  pass
  # parser = MTBParser()
  # for key in MTB_DIR:
    # print key
    # parser.load(key)
  # parser.load("dr2_mtb2_s01.pak")
  # parser.load("dr2_mtb2_s02.pak")
  # parser.load("dr2_mtb2_s03.pak")
  # parser.load("dr2_mtb2_s04.pak")
  # parser.load("dr2_mtb2_s05.pak")
  # parser.load("dr2_mtb2_s06.pak")
  # parser.load("dr2_mtb2_s07.pak")
  # parser.load("dr2_mtb2_s08.pak")
  # parser.load("dr2_mtb2_s09.pak")
  # parser.load("dr2_mtb2_s10.pak")
    
  # for x in range(1, 11):
    # data = ConstBitStream(filename = os.path.join(common.editor_config.data01_dir, BIN_DIR, "dr2_mtb2_s%02d.pak" % x))
    # with open("wip/mtb%02d.txt" % x, "wb") as f:
      # paks = [data for name, data in get_pak_files(data)]
      # for pak in paks:
        # for name, table in get_pak_files(pak):
          # for i in range(table.len / 16):
            # f.write("%6d " % table.read("intle:16"))
          # f.write("\n")
        # f.write("\n")
  
  # data = ConstBitStream(filename = os.path.join(common.editor_config.data01_dir, BIN_DIR, "dr2_mtb2_s02.pak"))

### EOF ###