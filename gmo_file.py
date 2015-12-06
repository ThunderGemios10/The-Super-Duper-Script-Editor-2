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

import logging
import os
import tempfile

from bitstring import BitStream, ConstBitStream
from gim_converter import GimConverter, QuantizeType

import common

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

GIM_MAGIC       = ConstBitStream(hex='0x4D49472E') # MIG.
GIM_SIZE_OFFSET = 0x14
# The size in the GIM excludes the first 0x10 bytes of the
# header, so we have to include them to get the whole thing.
GIM_SIZE_DIFF   = 0x10

GMO_MAGIC       = ConstBitStream(hex='0x4F4D472E') # OMG.
GMO_SIZE_OFFSET = 0x14
# The size in the GMO excludes the first 0x18 bytes of the
# header, so we have to include them to get the whole thing.
GMO_SIZE_DIFF   = 0x18

################################################################################
### Exceptions
################################################################################
class GimSizeError(Exception):
  pass

class GimIndexError(IndexError):
  pass

################################################################################
### A very simplified GMO parser, just intended to provide access
### to the GIM textures inside a model.
################################################################################
class GmoFile():
  def __init__(self, data = None, offset = 0, filename = None):
    self.data = None
    self.__gim_files = []
    
    self.gimconv = GimConverter()
    
    if not data == None:
      self.load_data(data, offset)
    elif not filename == None:
      self.load_file(filename)
  
  def load_file(self, filename):
    data = BitStream(filename = filename)
    self.load_data(data)
  
  def load_data(self, data, offset = 0):
    if not data[offset * 8 : offset * 8 + GMO_MAGIC.len] == GMO_MAGIC:
      _LOGGER.error("GMO header not found at 0x%04X." % offset)
      return
    
    data.bytepos = offset + GMO_SIZE_OFFSET
    gmo_size = data.read("uintle:32") + GMO_SIZE_DIFF
    
    self.data = BitStream(data[offset * 8 : (offset + gmo_size) * 8])
    
    self.__find_gims()
  
  def save(self, filename):
    with open(filename, "wb") as f:
      self.data.tofile(f)
  
  def __find_gims(self):
    if self.data == None:
      return
    
    self.__gim_files = []
    
    for gim_start in self.data.findall(GIM_MAGIC, bytealigned = True):
      gim_size_pos  = gim_start + (GIM_SIZE_OFFSET * 8) # Bit pos.
      gim_size      = self.data[gim_size_pos : gim_size_pos + 32].uintle + GIM_SIZE_DIFF
      
      # And turn it into a byte position.
      gim_start /= 8
      self.__gim_files.append((gim_start, gim_size))
  
  def gim_count(self):
    return len(self.__gim_files)
  
  def get_gim(self, gim_id):
    if gim_id >= self.gim_count():
      raise GimIndexError("Invalid GIM ID.")
    
    gim_start, gim_size = self.__gim_files[gim_id]
    gim_data = self.data[gim_start * 8 : (gim_start + gim_size) * 8]
    
    return gim_data
  
  def replace_png_file(self, gim_id, filename, quantize_to_fit = True):
  
    if quantize_to_fit:
      quantize_order = [QuantizeType.auto, QuantizeType.index8, QuantizeType.index4]
    else:
      quantize_order = [QuantizeType.auto]
    quantize_id = 0
    
    (fd, temp_gim) = tempfile.mkstemp(suffix = ".gim", prefix = "sdse-")
    os.close(fd) # Don't need the open file handle.
    
    while True:
      self.gimconv.png_to_gim(filename, temp_gim, quantize_order[quantize_id])
      
      try:
        self.replace_gim_file(gim_id, temp_gim)
      except GimSizeError:
        quantize_id += 1
      except GimIndexError:
        os.remove(temp_gim)
        raise
      else:
        # If we didn't except, that means we succeeded, so we can leave.
        _LOGGER.debug("Quantized PNG to %s" % quantize_order[quantize_id])
        break
      
      if quantize_id > len(quantize_order):
        _LOGGER.error("Unable to convert %s into a GIM small enough to insert." % filename)
        break
    
    os.remove(temp_gim)
  
  def replace_gim_file(self, gim_id, filename):
    gim_data = BitStream(filename = filename)
    self.replace_gim(gim_id, gim_data)
  
  def replace_gim(self, gim_id, gim_data):
    if gim_id >= self.gim_count():
      raise GimIndexError("Invalid GIM ID.")
    
    gim_start, gim_size = self.__gim_files[gim_id]
    
    if gim_data.len / 8 > gim_size:
      raise GimSizeError("GIM too large. %d bytes > %d bytes" % (gim_data.len / 8, gim_size))
      # return
    
    self.data.overwrite(gim_data, gim_start * 8)
    
    # Leave the length alone, though, because we know we have that much space
    # to work with from the original GIM file that was there, and there's no
    # point in shrinking that down if someone happens to want to re-replace
    # this GIM file without reloading the whole thing.
  
  def extract(self, directory, to_png = False):
    if not os.path.isdir(directory):
      os.makedirs(directory)
    
    for id in range(self.gim_count()):
      gim = self.get_gim(id)
      
      out_gim = os.path.join(directory, "%04d.gim" % id)
      out_png = os.path.join(directory, "%04d.png" % id)
      
      with open(out_gim, "wb") as f:
        gim.tofile(f)
      
      if to_png:
        self.gimconv.gim_to_png(out_gim, out_png)
        os.remove(out_gim)

if __name__ == "__main__":
  pass

### EOF ###