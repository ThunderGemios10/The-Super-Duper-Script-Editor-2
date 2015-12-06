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

EXTENSION_MAP = {
  ConstBitStream(bytes = "MIG.00.1PSP"):  ".gim",
  ConstBitStream(bytes = "LLFS"):         ".sfl",
  ConstBitStream(bytes = "RIFF"):         ".at3",
  ConstBitStream(bytes = "OMG.00.1PSP"):  ".gmo",
  ConstBitStream(hex = "0x89504E47"):     ".png",
  ConstBitStream(bytes = "BM"):           ".bmp",
  ConstBitStream(bytes = "VAGp"):         ".vag",
  ConstBitStream(bytes = "tFpS"):         ".font",
  ConstBitStream(hex = "0x41465332"):     ".awb",
  ConstBitStream(hex = "0xF0306090020000000C000000"): ".p3d",
}

EXTRACT_EXT = [".pak", ".lin", ".p3d", ".awb"]

##################################################
### 
##################################################
def guess_ext(data, file_start = 0, file_end = 0):
  
  extension = None
  
  file_len = file_end - file_start
  
  for magic in EXTENSION_MAP.keys():
    if file_len * 8 < magic.len:
      continue
    
    if data[file_start * 8 : (file_start * 8) + magic.len] == magic:
      extension = EXTENSION_MAP[magic]
      break
  
  return extension

### EOF ###