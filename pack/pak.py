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
from tempfile import TemporaryFile

import logging
import os
import shutil
import tempfile
import traceback

import common

from .awb import pack_awb
from .files import pack_file

from list_files import list_all_files
from wrd.wrd_file import WrdFile

P3D_MAGIC = ConstBitStream(hex = "0xF0306090")

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

CUSTOM_ALIGN = {
  "bin_anagram.pak":          (1, 1, False),
  "bin_break.pak":            (1, 1, False),
  "bin_break2.pak":           (1, 1, False),
  "bin_break_hanron.pak":     (1, 1, False),
  "bin_complete.pak":         (1, 1, False),
  "bin_complete2.pak":        (1, 1, False),
  "bin_complete_hanron.pak":  (1, 1, False),
  "bin_in_hanron.pak":        (1, 1, False),
}

def pack_dir(path, align_toc = 16, align_files = 16, eof = False):
  basename  = os.path.basename(path)
  name, ext = os.path.splitext(path)
  ext = ext.lower()
  
  if ext == ".lin":
    return pack_lin(path)
  
  elif ext == ".p3d":
    return P3D_MAGIC + pack_pak(path, align_toc = 12, align_files = 16)
  
  elif ext == ".awb":
    return pack_awb(path)
  
  elif basename in CUSTOM_ALIGN:
    align_toc, align_files, eof = CUSTOM_ALIGN[basename]
    return pack_pak(path, align_toc = align_toc, align_files = align_files, eof = eof)
  
  else:
    return pack_pak(path, align_toc = align_toc, align_files = align_files, eof = eof)

def pack_pak(dir, file_list = None, align_toc = 16, align_files = 16, eof = False):
  
  if file_list == None:
    file_list = sorted(os.listdir(dir))
    
  num_files  = len(file_list)
  toc_length = (num_files + 1) * 4
  
  if eof:
    toc_length += 1
  
  if toc_length % align_toc > 0:
    toc_length += align_toc - (toc_length % align_toc)
  
  archive_data = BitStream(uintle = 0, length = toc_length * 8)
  archive_data.overwrite(bitstring.pack("uintle:32", num_files), 0)
  
  for file_num, item in enumerate(file_list):
    full_path = os.path.join(dir, item)
    
    if os.path.isfile(full_path):
      data = pack_file(full_path)
    else:
      data = pack_dir(full_path, align_toc, align_files, eof)
    
    file_size = data.len / 8
    padding = 0
    
    if file_size % align_files > 0:
      padding = align_files - (file_size % align_files)
      data.append(BitStream(uintle = 0, length = padding * 8))
    
    file_pos = archive_data.len / 8
    archive_data.overwrite(bitstring.pack("uintle:32", file_pos), (file_num + 1) * 32)
    archive_data.append(data)
    
    del data
  
  if eof:
    archive_data.overwrite(bitstring.pack("uintle:32", archive_data.len / 8), (num_files + 1) * 32)
  
  return archive_data
  
def pack_lin(dir):
  
  # Collect our files.
  file_list = sorted(list_all_files(dir))
  
  txt = [filename for filename in file_list if os.path.splitext(filename)[1].lower() == ".txt"]
  wrd = [filename for filename in file_list if os.path.splitext(filename)[1].lower() == ".wrd"]
  py  = [filename for filename in file_list if os.path.splitext(filename)[1].lower() == ".py"]
  
  # If there are more than one for whatever reason, just take the first.
  # We only have use for a single wrd or python file.
  wrd = wrd[0] if wrd else None
  py  = py[0]  if py  else None
  
  # Prepare our temporary output directory.
  temp_dir = tempfile.mkdtemp(prefix = "sdse-")
  
  # Where we're outputting our wrd file, regardless of whether it's a python
  # file or a raw binary data file.
  wrd_dst = os.path.join(temp_dir, "0.wrd")
  
  if py:
    try:
      wrd_file = WrdFile(py)
    except:
      _LOGGER.warning("%s failed to compile. Parsing wrd file instead. Exception info:\n%s" % (py, traceback.format_exc()))
      shutil.copy(wrd, wrd_dst)
    else:
      # If we succeeded in loading the python file, compile it to binary.
      wrd_file.save_bin(wrd_dst)
  
  else:
    shutil.copy(wrd, wrd_dst)
  
  # Pack the text files in-place to save us a bunch of copying
  # and then move it to the tmp directory with the wrd file.
  if txt:
    data = pack_pak(dir, file_list = txt, eof = True)
    with open(os.path.join(temp_dir, "1.dat"), "wb") as f:
      data.tofile(f)
  
  # Then pack it like normal.
  data = pack_pak(temp_dir, eof = True)
  shutil.rmtree(temp_dir)
  
  return data

if __name__ == "__main__":
  pass

### EOF ###