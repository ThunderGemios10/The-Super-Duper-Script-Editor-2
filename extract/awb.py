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

AWB_MAGIC = ConstBitStream(hex = "0x41465332") # AFS2

##################################################
### 
##################################################
def get_awb_files(data, *args, **kwargs):
  
  magic = data.read(32)
  if not magic == AWB_MAGIC:
    print "Invalid AWB file."
    return
  
  unknown1    = data.read(32)
  num_entries = data.read("uintle:32")
  alignment   = data.read("uintle:32")
  
  file_ids  = []
  file_ends = []
  
  for i in range(num_entries):
    file_id = data.read("uintle:16")
    file_ids.append(file_id)
  
  header_end = data.read("uintle:32")
  for i in range(num_entries):
    file_end = data.read("uintle:32")
    file_ends.append(file_end)
  
  file_start = 0
  file_end   = header_end
  for i in range(num_entries):
    
    file_start = file_end
    if file_end % alignment > 0:
      file_start += (alignment - (file_end % alignment))
    file_end   = file_ends[i]
      
    filename = "%04d.at3" % (i + 1)
    out_data = data[file_start * 8 : file_end * 8]
    
    yield filename, out_data

##################################################
### 
##################################################
def extract_awb(filename, base_dir = "."):
  name, ext = os.path.splitext(os.path.basename(filename))
  out_dir = os.path.join(base_dir, name)# + "-out"
  
  if not os.path.isdir(out_dir):
    os.makedirs(out_dir)
  
  data = ConstBitStream(filename = filename)
  
  for filename, file_data in get_awb_files(data):
    out_path = os.path.join(out_dir, filename)
    
    with open(out_path, "wb") as out_file:
      file_data.tofile(out_file)
  
##################################################
### 
##################################################
if __name__ == "__main__":
  extract_awb("voice.awb")

### EOF ###