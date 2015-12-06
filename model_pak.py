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

from bitstring import BitStream, ConstBitStream

from extract.pak import get_pak_files, parse_pak_toc
from gmo_file import GmoFile, GMO_MAGIC

import common

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

_NAME  = "Name"
_START = "Start"
_SIZE  = "Size"
_DATA  = "Data"

class ModelPak():
  
  def __init__(self, filename = None):
    self.__data = None
    self.__gmo_files = []
    
    if filename:
      self.load_file(filename)
  
  def load_file(self, filename):
    data = BitStream(filename = filename)
    self.load_data(data)
  
  def load_data(self, data):
    files = [entry_data for (entry_name, entry_data) in get_pak_files(data)]
    
    # There are always at least four files in a model pak.
    # The first three I don't know a lot about, and then
    # the GMO files come after that.
    if len(files) < 4:
      _LOGGER.error("Invalid model PAK. %d files found, but at least 4 needed." % len(files))
      return
    
    # The name pak contains a list of null-terminated names for
    # each of the models, stored in our standard pak format.
    name_pak = files[0]
    names    = [entry_data.bytes.strip('\0') for (entry_name, entry_data) in get_pak_files(name_pak)]
    
    # Most of the model paks in SDR2 have a fourth unknown file before the models
    # start, so we'll just take everything from the back end and call it a day.
    models = files[-len(names):]
    
    # Now, we don't get file positions from the unpacker, so let's find those
    # and start filling out our internal list of GMO files.
    file_starts, file_ends = parse_pak_toc(data)
    model_starts = file_starts[-len(names):]
    
    for i, model in enumerate(models):
      # First of all, not all of the "models" present are actually GMO files.
      # It's rare, but there is the occasional other unknown format.
      # So let's make sure we have a GMO file.
      if not model[:GMO_MAGIC.len] == GMO_MAGIC:
        # print i, "Not a GMO."
        continue
      
      name  = names[i]
      gmo   = GmoFile(data = model)
      size  = model.len / 8
      start = model_starts[i]
      
      self.__gmo_files.append({
        _NAME:   name,
        _START:  start,
        _SIZE:   size,
        _DATA:   gmo,
      })
    
    self.__data = BitStream(data)
  
  def save(self, filename):
    self.__update_data()
    with open(filename, "wb") as f:
      self.__data.tofile(f)
  
  def __update_data(self):
    for gmo in self.__gmo_files:
      start = gmo[_START] * 8
      data  = gmo[_DATA].data
      
      self.__data.overwrite(data, start)
  
  def get_data(self):
    self.__update_data()
    return self.__data
  
  def gmo_count(self):
    return len(self.__gmo_files)
    
  def get_gmo(self, index):
    if index >= self.gmo_count() or index == None:
      _LOGGER.error("Invalid GMO ID %d." % index)
      return None
    
    return self.__gmo_files[index][_DATA]
  
  def get_gmos(self):
    return [gmo[_DATA] for gmo in self.__gmo_files]
  
  def get_name(self, index):
    if index >= self.gmo_count():
      _LOGGER.error("Invalid GMO ID %d." % index)
      return None
    
    return self.__gmo_files[index][_NAME]
  
  def get_names(self):
    return [gmo[_NAME] for gmo in self.__gmo_files]
  
  def id_from_name(self, name):
    for i in range(self.gmo_count()):
      if self.__gmo_files[i][_NAME] == name:
        return i
    
    return None
  
  def gmo_from_name(self, name):
    id = self.id_from_name(name)
    
    if id:
      return self.get_gmo(id)
    else:
      return None
  
  def replace_gmo_file(self, index, filename):
    gmo = GmoFile(filename = filename)
    self.replace_gmo(index, gmo)
    
  def replace_gmo(self, index, new_gmo):
    if index >= self.gmo_count():
      _LOGGER.error("Invalid GMO ID %d." % index)
      return None
    
    gmo = self.__gmo_files[index]
    
    if new_gmo.data.len / 8 > gmo[_SIZE]:
      _LOGGER.error("GMO too large to insert. %d bytes > %d bytes" % (new_gmo.data.len / 8, gmo[_SIZE]))
      return
    
    self.__gmo_files[index][_DATA] = new_gmo
    
    # Leave the length alone, though, because we know we have that much space
    # to work with from the original GMO file that was there, and there's no
    # point in shrinking that down if someone happens to want to re-replace
    # this GMO file without reloading the whole thing.
  
  def extract(self, directory, to_png = False):
    if not os.path.isdir(directory):
      os.makedirs(directory)
    
    for id in range(self.gmo_count()):
      gmo  = self.get_gmo(id)
      name = self.get_name(id)
      
      if gmo.gim_count() == 0:
        continue
      
      out_dir = os.path.join(directory, name)
      gmo.extract(out_dir, to_png)

if __name__ == "__main__":
  import glob
  # for file in glob.iglob("X:/Danganronpa/Danganronpa_BEST/umdimage2-nor/bg_*.pak"):
    # basename = os.path.basename(file)
    # out_dir = os.path.join("X:/Danganronpa/Danganronpa_BEST/umdimage2-imgediting2", basename)
    
    # pak = ModelPak(filename = file)
    # pak.extract(out_dir)
  
  for pak_dir in glob.iglob("X:/Danganronpa/Danganronpa_BEST/image-editing/umdimage2-vodka-png/bg_*.pak"):
    basename = os.path.basename(pak_dir)
    
    pak = ModelPak(filename = os.path.join("X:/Danganronpa/Danganronpa_BEST/umdimage2-orig", basename))
    
    for gmo_name in os.listdir(pak_dir):
      gmo_id = pak.id_from_name(gmo_name)
      gmo    = pak.get_gmo(gmo_id)
      
      for gim in os.listdir(os.path.join(pak_dir, gmo_name)):
        name, ext = os.path.splitext(gim)
        
        if not ext == ".gim":
          continue
        
        print os.path.join(basename, gmo_name, gim)
        gim_id = int(name)
        
        gmo.replace_gim_file(gim_id, os.path.join(pak_dir, gmo_name, gim))
      
      pak.replace_gmo(gmo_id, gmo)
    
    pak.save(os.path.join("X:/Danganronpa/Danganronpa_BEST/image-editing/umdimage2-vodka", basename))
      
      # print gmo_name, gmo_id
    # pak = ModelPak(filename = "X:/Danganronpa/Danganronpa_BEST/umdimage2-orig/bg_101.pak")
  # id  = pak.id_from_name("bg_001_p04")
  # gmo = pak.get_gmo(id)
  
  # gmo.replace_gim_file(13,  "X:/Danganronpa/Danganronpa_BEST/image-editing/umdimage2-vodka-png/bg_018.pak/bg_001_p04/0013.gim")
  # gmo.replace_gim_file(19, "X:\\Danganronpa\\Danganronpa_BEST\\image-editing\\Models\\!done\\0166_bg_160.pak\\0007\\0024-2-fs8.gim")
  # gmo.replace_gim_file(20, "X:\\Danganronpa\\Danganronpa_BEST\\image-editing\\Models\\!done\\0166_bg_160.pak\\0007\\0025-2-fs8.gim")
  # gmo.replace_gim_file(21, "X:\\Danganronpa\\Danganronpa_BEST\\image-editing\\Models\\!done\\0166_bg_160.pak\\0007\\0026-2-fs8.gim")
  # gmo.replace_gim_file(22, "X:\\Danganronpa\\Danganronpa_BEST\\image-editing\\Models\\!done\\0166_bg_160.pak\\0007\\0027-2-fs8.gim")
  # pak.replace_gmo(4, gmo)
  # pak.save("debug/bg_101.pak")
  
  # pak.extract("debug/bg_101", to_png = False)

### EOF ###