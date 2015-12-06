################################################################################
### Copyright © 2012-2013 BlackDragonHunt
### Copyright © 2012-2013 /a/nonymous scanlations
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

from wrd.ops import *

from wrd.bin import to_bin, from_bin
from wrd.python import to_python, from_python
from wrd.scene import to_scene_info

################################################################################
### A meta class for easy access to the relevant wrd parsing/converting fns,
### plus some helper functions for use in the editor.
################################################################################
class WrdFile:
  def __init__(self, filename = None):
    
    self.commands = []
    
    if not filename == None:
      if os.path.splitext(filename)[1].lower() == ".py":
        self.load_python(filename)
      else:
        self.load_bin(filename)
  
  ##############################################################################
  ### Binary
  ##############################################################################
  def load_bin(self, filename):
    data = ConstBitStream(filename = filename)
    self.from_bin(data)
  
  def save_bin(self, filename):
    data = self.to_bin()
    with open(filename, "wb") as f:
      data.tofile(f)
  
  def from_bin(self, data):
    self.commands = from_bin(data)
  
  def to_bin(self):
    return to_bin(self.commands)
  
  ##############################################################################
  ### Python
  ##############################################################################
  def load_python(self, filename):
    script = ""
    
    with open(filename, "rb") as f:
      script = f.read()
    
    self.from_python(script)
  
  def save_python(self, filename):
    script = self.to_python()
    with open(filename, "wb") as f:
      f.write(script)
  
  def from_python(self, script):
    self.commands = from_python(script)
    
  def to_python(self):
    return to_python(self.commands)
  
  ##############################################################################
  ### SceneInfo
  ##############################################################################
  def to_scene_info(self):
    return to_scene_info(self.commands)
  
  ##############################################################################
  ### Helper functions
  ##############################################################################
  def num_lines(self):
    lines = 0
    
    for op, params in self.commands:
      if op == WRD_SHOW_LINE:
        lines += 1
    
    return lines
  
  def max_line(self):
    max = 0
    
    for op, params in self.commands:
      if op == WRD_SHOW_LINE and params["line"] > max:
        max = params["line"]
    
    return max
  
  def insert_line_after(self, insert_after):
    self.insert_line(insert_after, before = False)
  
  def insert_line_before(self, insert_before):
    self.insert_line(insert_before, before = True)
  
  ######################################################################
  ### Inserts a new line relative to the target line.
  ######################################################################
  def insert_line(self, target, before = False):
    
    found    = False
    new_line = self.max_line() + 1
    index    = 0
    
    for i, (op, params) in enumerate(self.commands):
      if op == WRD_SHOW_LINE and params["line"] == target:
        found = True
        
        # If we're inserting before a line, then just take this index and go.
        if before:
          index = i
          break
      
      # If we're inserting after a line, though, wait until we find the nearest
      # wait-for-input command and insert after that.
      if op == WRD_WAIT_INPUT and found:
        index = i + 1
        break
    
    if not found:
      raise Exception("Could not insert line. Reference line %d does not exist." % target)
    
    # Insert our command backwards so we don't have to worry about index shifting.
    self.commands.insert(index, (WRD_WAIT_INPUT, {}))
    self.commands.insert(index, (WRD_WAIT_FRAME, {"frames": 1}))
    self.commands.insert(index, (WRD_SHOW_LINE,  {"line": new_line}))
    
    return new_line

def main():
  
  import glob
  import time

  # wrds = glob.iglob("wrds-sdr2/e00*.wrd")
  # pys  = glob.iglob("wrds-sdr2/e00*.py")
  wrds = glob.iglob("wip/wrds-sdr2/e01*.wrd")
  # pys  = glob.iglob("wip/wrds-sdr2/*.py")
  
  wrd = WrdFile()
  
  # start = time.time()
  # for filename in wrds:
    # wrd.load_bin(filename)
  # print "Took", time.time() - start, "seconds to parse wrds."
  
  # start = time.time()
  # for filename in pys:
    # wrd.load_python(filename)
    # wrd_file = os.path.splitext(filename)[0]# + ".wrd"
    # wrd.save_bin(wrd_file)
  # print "Took", time.time() - start, "seconds to parse pys."
  
  # return
  
  for filename in wrds:
    
    print filename
    
    orig = ConstBitStream(filename = filename)
    test = WrdFile(filename)
    
    # if test.num_lines() > 0:
      # script = test.to_python()
      # with open(filename + "-1.py", "wb") as f:
        # f.write(script)
      
      # test.insert_line(0)
      # script = test.to_python()
      # with open(filename + "-2.py", "wb") as f:
        # f.write(script)
    
    script = test.to_python()
    with open(filename + ".py", "wb") as f:
      f.write(script)
    test.from_python(script)
    out = test.to_bin()
    
    if not orig == out:
      # print filename
      print "  Didn't match!"
    
      with open(filename + "-out", "wb") as f:
        out.tofile(f)
      
      with open(filename + ".py", "wb") as f:
        f.write(script)
  
if __name__ == "__main__":
  main()

### EOF ###