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
import os
import time
import re

from .cpk_dec import decompress_cpk

from .awb import AWB_MAGIC, get_awb_files
from .ext import EXTRACT_EXT
from .pak import *
# from .p3d import get_p3d_files

############################################################
### CONSTANTS
############################################################
CPK_MAGIC      = ConstBitStream(hex = "0x43504B20") # "CPK "
TOC_MAGIC      = ConstBitStream(hex = "0x544F4320") # "TOC "
UTF_MAGIC      = ConstBitStream(hex = "0x40555446") # "@UTF"

COLUMN_STORAGE_MASK        = 0xf0
COLUMN_STORAGE_PERROW      = 0x50
COLUMN_STORAGE_CONSTANT    = 0x30
COLUMN_STORAGE_ZERO        = 0x10
COLUMN_TYPE_MASK           = 0x0f
COLUMN_TYPE_DATA           = 0x0b
COLUMN_TYPE_STRING         = 0x0a
COLUMN_TYPE_FLOAT          = 0x08
COLUMN_TYPE_8BYTE2         = 0x07
COLUMN_TYPE_8BYTE          = 0x06
COLUMN_TYPE_4BYTE2         = 0x05
COLUMN_TYPE_4BYTE          = 0x04
COLUMN_TYPE_2BYTE2         = 0x03
COLUMN_TYPE_2BYTE          = 0x02
COLUMN_TYPE_1BYTE2         = 0x01
COLUMN_TYPE_1BYTE          = 0x00

SKIP_EXTRACT_FILE_RE = re.compile(ur"dr2_mtb2_s\d\d|hs_mtb_s\d\d|logicaldive_level\d\d|anagram2_config|trial_camera|bin_progress_data_param")
SKIP_EXTRACT_DIR_RE  = re.compile(ur"modelbg")

FILE_NORECURSIVE_RE  = re.compile(ur"effect_lensflare00")

# THIS FEELS SO HACKY
# pattern, function, special arguments = list of (keyword, template for match.expand())
SPECIAL_FILE_EXTRACT = [
  (re.compile(ur"bin_.*?_font_l.pak$"),           get_bin_txt_files,    []),
  (re.compile(ur"twilight_all.pak$"),             get_bin_txt_files,    []),
  (re.compile(ur"(script_pak_.*?)\.pak$"),        get_script_pak_files, [(u"lin_name", ur"\1")]),
  (re.compile(ur"(e\d\d.*?|novel_\d\d\d)\.lin$"), get_lin_files,        [(u"lin_name", ur"\1")]),
  (re.compile(ur"\.p3d$"),                        get_p3d_files,        []),
  (re.compile(ur"\.awb$"),                        get_awb_files,        []),
  (re.compile(ur"\.pak$"),                        get_pak_files,        []),
]

############################################################
### FUNCTIONS
############################################################

##################################################
### 
##################################################
def dump_to_file(data, filename):
  dirname = os.path.dirname(filename)
  try:
    os.makedirs(dirname)
  except: pass
  
  with open(filename, "wb") as out_file:
    data.tofile(out_file)

##################################################
### 
##################################################
def query_utf(data, table_offset, index, name):
  table_offset += 0x10
  
  old_pos = data.bytepos
  data.bytepos = table_offset
  
  magic = data.read(32)
  if not magic == UTF_MAGIC:
    data.bytepos = old_pos
    print "Not a @UTF table at %d" % table_offset
    return
  
  table_size        = data.read("uint:32")
  schema_offset     = 0x20
  rows_offset       = data.read("uint:32")
  str_table_offset  = data.read("uint:32")
  data_offset       = data.read("uint:32")
  table_name_string = data.read("uint:32")
  columns           = data.read("uint:16")
  row_width         = data.read("uint:16")
  rows              = data.read("uint:32")
  #print table_size, schema_offset, rows_offset, str_table_offset, data_offset, table_name_string, columns, row_width, rows
  
  schema_info = []
  
  for i in range(columns):
    schema_type  = data.read("uint:8")
    col_name     = data.read("uint:32")
    const_offset = -1
    
    if schema_type & COLUMN_STORAGE_MASK == COLUMN_STORAGE_CONSTANT:
      const_offset = data.bytepos
      
      data_type = schema_type & COLUMN_TYPE_MASK
      if data_type in [COLUMN_TYPE_DATA, COLUMN_TYPE_8BYTE2, COLUMN_TYPE_8BYTE]:
        data.read(64)
      elif data_type in [COLUMN_TYPE_STRING, COLUMN_TYPE_FLOAT, COLUMN_TYPE_4BYTE2, COLUMN_TYPE_4BYTE]:
        data.read(32)
      elif data_type in [COLUMN_TYPE_2BYTE2, COLUMN_TYPE_2BYTE]:
        data.read(16)
      elif data_type in [COLUMN_TYPE_1BYTE2, COLUMN_TYPE_1BYTE]:
        data.read(8)
      else:
        data.bytepos = old_pos
        print "Unknown type for constant."
        return
    
    schema_info.append((schema_type, col_name, const_offset))
  
  str_table_start = str_table_offset + 8 + table_offset
  str_table_size  = data_offset - str_table_offset
  str_table_end   = str_table_start + str_table_size
  str_table = data[str_table_start * 8 : str_table_end * 8]
  #print str_table_start, str_table_size
  
  for i in range(index, rows):
    row_offset = table_offset + 8 + rows_offset + (i * row_width)
    #print row_offset
    
    for j in range(columns):
      schema_type  = schema_info[j][0]
      col_name     = schema_info[j][1]
      const_offset = schema_info[j][2]
      
      if const_offset >= 0:
        data_offset = const_offset
      else:
        data_offset = row_offset
      
      if schema_type & COLUMN_STORAGE_MASK == COLUMN_STORAGE_ZERO:
        value = 0
      else:
        data.bytepos = data_offset
        
        type_mask = schema_type & COLUMN_TYPE_MASK
        if type_mask == COLUMN_TYPE_STRING:
          str_offset = data.read("uint:32")
          str_table.bytepos = str_offset
          value = str_table.readto("0x00", bytealigned = True).bytes[:-1]
        
        elif type_mask == COLUMN_TYPE_DATA:
          vardata_offset = data.read("uint:32")
          vardata_size   = data.read("uint:32")
          str_table.bytepos = vardata_offset
          value = str_table.read(vardata_size)
        
        elif type_mask == COLUMN_TYPE_FLOAT:
          value = data.read("float:32")
        elif type_mask == COLUMN_TYPE_8BYTE2:
          value = data.read("uint:64")
        elif type_mask == COLUMN_TYPE_8BYTE:
          value = data.read("uint:64")
        elif type_mask == COLUMN_TYPE_4BYTE2:
          value = data.read("uint:32")
        elif type_mask == COLUMN_TYPE_4BYTE:
          value = data.read("uint:32")
        elif type_mask == COLUMN_TYPE_2BYTE2:
          value = data.read("uint:16")
        elif type_mask == COLUMN_TYPE_2BYTE:
          value = data.read("uint:16")
        elif type_mask == COLUMN_TYPE_1BYTE2:
          value = data.read("uint:8")
        elif type_mask == COLUMN_TYPE_1BYTE:
          value = data.read("uint:8")
        else:
          data.bytepos = old_pos
          print "Unknown normal type."
          return
        
        if const_offset < 0:
          row_offset = data.bytepos
      ### endif ###
      
      str_table.bytepos = col_name
      col_name = str_table.readto("0x00", bytealigned = True).bytes[:-1]
      
      if col_name == name:
        data.bytepos = old_pos
        return value
  
  data.bytepos = old_pos
  return ""

##################################################
### 
##################################################
def get_cpk_files(data):
  
  cpk_magic = data.read(32)
  if not cpk_magic == CPK_MAGIC:
    print "Invalid CPK file."
    return
  
  toc_offset     = query_utf(data, 0, 0, "TocOffset")
  content_offset = query_utf(data, 0, 0, "ContentOffset")
  num_files      = query_utf(data, 0, 0, "Files")
  print toc_offset, content_offset, num_files
  
  data.bytepos = toc_offset
  toc_magic = data.read(32)
  if not toc_magic == TOC_MAGIC:
    print "TOC signature not found"
    return
  
  # The CPK QuickBMS script re-queries the TOC table and stores
  # the number of rows here. In the files I've messed with,
  # the value of "Files" from the normal table = rows,
  # and I'd have to be kind of hacky to access the value of
  # rows the way the code's currently laid out, so doing this instead.
  toc_entries = num_files
  
  add_offset = 0
  if content_offset < 0:
    add_offset = toc_offset
  elif toc_offset < 0:
    add_offset = content_offset
  elif content_offset < toc_offset:
    add_offset = content_offset
  else:
    add_offset = toc_offset
  
  print "  offset   filesize   filename"
  print "------------------------------"
  
  for row in range(toc_entries):
    dirname  = query_utf(data, toc_offset, row, "DirName")
    filename = query_utf(data, toc_offset, row, "FileName")
    
    file_size    = query_utf(data, toc_offset, row, "FileSize")
    extract_size = query_utf(data, toc_offset, row, "ExtractSize")
    file_offset  = query_utf(data, toc_offset, row, "FileOffset")
    
    file_offset += add_offset
    
    #print dirname, filename, file_size, extract_size, file_offset
    print "  %08x %-10d %s" % (file_offset, extract_size, dirname + "/" + filename)
    
    out_data = data[file_offset * 8 : (file_offset + file_size) * 8]
    if extract_size > file_size:
      out_data = decompress_cpk(out_data, extract_size)
    
    yield dirname, filename, out_data

##################################################
### 
##################################################
def extract_cpk(filename, out_dir = None):
  name, ext = os.path.splitext(filename)
  
  if out_dir == None:
    out_dir = name #+ "-test-dec"
  
  data = ConstBitStream(filename = filename)
  
  for dirname, filename, file_data in get_cpk_files(data):
    final_dir = os.path.join(out_dir, dirname)
    try:
      os.makedirs(final_dir)
    except: pass
    
    out_path = os.path.join(final_dir, filename)
    
    name, ext = os.path.splitext(filename)
    basename = os.path.basename(dirname)
    
    ext = ext.lower()
    basename = basename.lower()
    
    if ext in EXTRACT_EXT and SKIP_EXTRACT_FILE_RE.search(filename) == None and SKIP_EXTRACT_DIR_RE.search(basename) == None:
      try:
        extract_fn = get_pak_files
        file_ext = None
        ext_mode = EXT_MODE.auto
        recursive = True
        
        kwargs = {}
        
        if FILE_NORECURSIVE_RE.search(filename):
          recursive = False
        
        for regex, fn, args in SPECIAL_FILE_EXTRACT:
          match = regex.search(filename)
          if match:
            extract_fn = fn
            for name, template in args:
              kwargs[name] = match.expand(template)
            break
        
        if basename == "script":
          file_ext = ".txt"
          ext_mode = EXT_MODE.force
        
        kwargs["recursive"] = recursive
        kwargs["file_ext"]  = file_ext
        kwargs["ext_mode"]  = ext_mode
        # for sub_filename, sub_data in extract_fn(file_data, recursive, file_ext, ext_mode):
        for sub_filename, sub_data in extract_fn(file_data, **kwargs):
          dump_to_file(sub_data, os.path.join(out_path, sub_filename))
        
      except InvalidArchiveException:
        dump_to_file(file_data, out_path)
    
    else:
      dump_to_file(file_data, out_path)
  # for dirname, filename, file_data in get_cpk_files(data)
  
##################################################
### 
##################################################
if __name__ == "__main__":
  import sys
  cpk = "data01.cpk"
  dir = None
  
  if len(sys.argv) > 1:
    cpk = sys.argv[1].decode(sys.stdin.encoding)
    
    if len(sys.argv) > 2:
      dir = sys.argv[2].decode(sys.stdin.encoding)
    
  start = time.time()
  extract_cpk(cpk, dir)
  elapsed = time.time() - start
  print "Took %d seconds to extract." % elapsed

### EOF ###