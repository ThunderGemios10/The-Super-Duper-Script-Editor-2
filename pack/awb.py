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
_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

from list_files import list_all_files

AWB_MAGIC = BitStream(hex = "0x41465332") # AFS2
AWB_UNK   = BitStream(hex = "0x01040200") # Both files I have use this, so.
AWB_ALIGN = 0x20

def pack_awb(dir):
  file_list  = sorted(os.listdir(dir))
  file_count = len(file_list)
  
  file_end_offset = 0x10 + (2 * file_count)
  
  data = AWB_MAGIC + \
         AWB_UNK + \
         bitstring.pack("uintle:32, uintle:32", file_count, AWB_ALIGN) + \
         bitstring.pack(", ".join(["uintle:16=%d" % id for id in range(file_count)])) + \
         BitStream(uintle = 0, length = (file_count + 1) * 32)
         # Plus one for the header.
  
  for i, file in enumerate(file_list):
    file_end = data.len / 8
    data.overwrite(bitstring.pack("uintle:32", file_end), (file_end_offset + (i * 4)) * 8)
    
    padding = 0
    if file_end % AWB_ALIGN > 0:
      padding = AWB_ALIGN - (file_end % AWB_ALIGN)
      data.append(BitStream(uintle = 0, length = padding * 8))
    
    file_data = ConstBitStream(filename = os.path.join(dir, file))
    data.append(file_data)
  
  # One last file end.
  file_end = data.len / 8
  data.overwrite(bitstring.pack("uintle:32", file_end), (file_end_offset + (file_count * 4)) * 8)
  
  return data

if __name__ == "__main__":
  pass

### EOF ###