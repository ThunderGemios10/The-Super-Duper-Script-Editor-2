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
from enum import Enum

import os

from .ext import guess_ext
from .invalidarchiveexception import *

EXT_MODE = Enum("force", "suggest", "auto")
DEFAULT_EXT = ".dat"

NULL_BYTE = ConstBitStream(hex = "0x00")
P3D_MAGIC = ConstBitStream(hex = "0xF0306090")

##################################################
### 
##################################################
def parse_pak_toc(data):
  
  # If we don't have enough to even get a file count, we're obviously no good.
  if data.len < 32:
    raise InvalidArchiveException
    
  data.bytepos = 0
  
  num_files = data.read("uintle:32")
  # One extra for the file count.
  toc_len = (num_files + 1) * 4
  
  if num_files <= 0 or toc_len >= data.len / 8:
    raise InvalidArchiveException
  
  file_starts = []
  file_ends   = []
  
  for i in xrange(num_files):
    file_start = data.read("uintle:32")
    
    # Obviously, a file can't start after the end of the archive
    # or inside the table of contents.
    if file_start < toc_len or file_start >= data.len / 8:
      raise InvalidArchiveException
      
    # Doesn't make much sense if they're not in order.
    if i > 0 and file_start < file_starts[-1]:
      raise InvalidArchiveException
    
    file_starts.append(file_start)
  
  for i in xrange(num_files):
  
    file_start = file_starts[i]
    if i == num_files - 1:
      file_end = (data.len / 8)
    else:
      file_end = file_starts[i + 1]
    
    file_ends.append(file_end)
  
  return file_starts, file_ends

##################################################
### 
##################################################
def get_pak_files(data, recursive = False, file_ext = None, ext_mode = EXT_MODE.suggest, toc = None):
  
  # If we don't have enough to even get a file count, we're obviously no good.
  if data.len < 32:
    raise InvalidArchiveException
  
  file_starts = []
  file_ends   = []
  filenames   = None
  
  if toc == None:
    
    file_starts, file_ends = parse_pak_toc(data)
    num_files = len(file_starts)
  
  else:
    
    num_files = data.read("uintle:32")
    
    filenames = []
    for entry in toc:
      file_pos = entry["file_pos"]
      file_end = file_pos + entry["file_len"]
      filename = entry["filename"]
      
      file_starts.append(file_pos)
      file_ends.append(file_end)
      filenames.append(filename)
  
  ### if toc == None ###
  
  for i in xrange(num_files):
    
    file_start  = file_starts[i]
    file_end    = file_ends[i]
    
    try:
      filename, extension = os.path.splitext(filenames[i])
      
    except TypeError, IndexError:
      filename = "%04d" % i
      extension = None
      
      if ext_mode == EXT_MODE.auto or ext_mode == EXT_MODE.suggest:# or file_ext == None:
        extension = guess_ext(data, file_start, file_end)
        
      if ext_mode == EXT_MODE.force or (ext_mode == EXT_MODE.suggest and extension == None):
        extension = file_ext
    
    # Look for a null character signifying the end of text data,
    # so we don't end up with any left-over junk or extra nulls.
    # Since text is UTF-16, we check two bytes at a time.
    if extension == ".txt":
      txt_end = file_end
      for txt_byte in xrange(file_start * 8, file_end * 8, 16):
        if data[txt_byte : txt_byte + 8] == NULL_BYTE and data[txt_byte + 8 : txt_byte + 16] == NULL_BYTE:
          txt_end = (txt_byte / 8) + 2
          break
      file_end = txt_end
    
    file_data = data[file_start * 8 : file_end * 8]
    
    # print file_start, file_end, filename, extension
    
    if extension == None:
      if recursive == True:
        try:
          for subfile, subdata in get_pak_files(file_data, True, None):
            full_filename = os.path.join(filename, subfile)
            yield full_filename, subdata
        except InvalidArchiveException:
          extension = DEFAULT_EXT
      else:
        extension = DEFAULT_EXT
    
    if extension == ".p3d" and recursive == True:
      filename = filename + extension
      for subfile, subdata in get_p3d_files(file_data, recursive):
        full_filename = os.path.join(filename, subfile)
        yield full_filename, subdata
    
    elif not extension == None:
      filename = filename + extension
      yield filename, file_data
  
  ### for i in xrange(num_files) ###

##################################################
### 
##################################################
def get_p3d_files(data, *args, **kwargs):
  
  # p3d is just a pak with an extra 0xF0306090 at the start.
  magic = data.read(P3D_MAGIC.len)
  if not magic == P3D_MAGIC:
    raise InvalidArchiveException("Invalid P3D file.")
  
  data = data[magic.len:]
  
  for filename, file_data in get_pak_files(data, *args, **kwargs):
    yield filename, file_data

##################################################
### Recursive/file_ext aren't actually used.
### They're just stupid placeholders to let me use
### various functions interchangeably in extract_pak.
##################################################
def get_lin_files(data, lin_name = "noname", *args, **kwargs):
  
  lin_data = list(get_pak_files(data, False))
  
  try:
    wrd_filename, wrd_data = lin_data[0]
  except:
    raise InvalidArchiveException
  
  try:
    txt_dirname, txt_data = lin_data[1]
  except:
    txt_dirname, txt_data = None, None
  
  wrd_filename = os.path.dirname(wrd_filename)
  if lin_name:
    wrd_filename = os.path.join(wrd_filename, "%s.scp.wrd" % lin_name)
  
  yield wrd_filename, wrd_data
  
  if not txt_dirname == None and not txt_data == None:
    txt_dirname = os.path.dirname(txt_dirname)
    
    for txt_filename, txt_subdata in get_pak_files(txt_data, False, ".txt", EXT_MODE.force):
      txt_filename = os.path.join(txt_dirname, txt_filename)
      yield txt_filename, txt_subdata

##################################################
### Recursive/file_ext aren't actually used.
### They're just stupid placeholders to let me use
### various functions interchangeably in extract_pak.
##################################################
def get_script_pak_files(data, lin_name, *args, **kwargs):
  
  for lin_file, lin_data in get_pak_files(data, False, "", EXT_MODE.force):
    sub_lin_name = "%s_%03d" % (lin_name, int(lin_file))
    lin_file = sub_lin_name + ".lin"
    
    for out_file, out_data in get_lin_files(lin_data, lin_name = sub_lin_name):
      out_file = os.path.join(lin_file, out_file)
      yield out_file, out_data

##################################################
### Recursive/file_ext aren't actually used.
### They're just stupid placeholders to let me use
### various functions interchangeably in extract_pak.
##################################################
def get_bin_txt_files(data, *args, **kwargs):
  
  for pak_file, pak_data in get_pak_files(data, False, ".pak", EXT_MODE.force):
    # Suggest because there are some with mixed data types.
    for out_file, out_data in get_pak_files(pak_data, False, ".txt", EXT_MODE.suggest):
      out_file = os.path.join(pak_file, out_file)
      yield out_file, out_data

##################################################
### Recursive/file_ext aren't actually used.
### They're just stupid placeholders to let me use
### various functions interchangeably in extract_pak.
##################################################
def get_txt_files(data, *args, **kwargs):
  
  for pak_file, pak_data in get_pak_files(data, False, ".txt", EXT_MODE.force):
    yield pak_file, pak_data

##################################################
### 
##################################################
def extract_pak(filename, out_dir = None, get_files_fn = get_pak_files, file_ext = None, recursive = True, *args, **kwargs):
  if out_dir == None:
    out_dir = filename + "-out"
  
  data = ConstBitStream(filename = filename)
  
  kwargs["recursive"] = recursive
  kwargs["file_ext"]  = file_ext
  for filename, file_data in get_files_fn(data, *args, **kwargs):
    out_path = os.path.join(out_dir, filename)
    
    # print filename
    
    final_dir = os.path.dirname(out_path)
    try:
      os.makedirs(final_dir)
    except: pass
    
    with open(out_path, "wb") as out_file:
      file_data.tofile(out_file)
  
##################################################
### 
##################################################
# if __name__ == "__main__":
  # extract_pak("bin_help_font_l.pak", get_files_fn = get_bin_txt_files)
  # extract_pak("bin_pb_font_l.pak", get_files_fn = get_bin_txt_files)
  # extract_pak("bin_progress_font_l.pak", get_files_fn = get_bin_txt_files)
  # extract_pak("bin_special_font_l.pak", get_files_fn = get_bin_txt_files)
  # extract_pak("bin_sv_font_l.pak", get_files_fn = get_bin_txt_files)
  # extract_pak("twilight_all.pak", get_files_fn = get_bin_txt_files)
  # extract_pak("bgm.pak", recursive = False)
  # extract_pak("voice_trial.pak", recursive = False)

### EOF ###