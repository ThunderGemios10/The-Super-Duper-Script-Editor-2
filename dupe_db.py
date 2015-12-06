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

from csv import DictReader, DictWriter
from collections import defaultdict
import codecs
import hashlib
import logging
import os.path
import sys
import shutil

import common
import dir_tools

file_list = []
GROUP_SIZES = {}

CSV_FILE = common.editor_config.dupes_csv

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

################################################################################
### SOME FUNCTIONS
################################################################################

class DupesDB:
  def __init__(self, csv_file = CSV_FILE):
    
    self.dupes = defaultdict(set)
    self.csv_file = csv_file
    
    self.load_csv(self.csv_file)
  
  def load_csv(self, csv_file = None):
    if csv_file == None:
      csv_file = self.csv_file
    
    self.dupes.clear()

    # Load in our CSV.
    dupes_csv = DictReader(open(csv_file, 'rb'))

    for row in dupes_csv:
      group     = int(row['Group'])
      filename  = dir_tools.normalize(row['File'])
      
      self.dupes[group].add(filename)
  
  def save_csv(self, csv_file = None):
    if csv_file == None:
      csv_file = self.csv_file
    
    dupes_csv = DictWriter(open(csv_file, 'wb'), fieldnames = ['Group', 'File'])
    dupes_csv.writerow({'Group':'Group', 'File':'File'})
    
    for group in sorted(self.dupes.keys()):
      files = self.dupes[group]
      
      # No point in keeping it if there aren't at least two files.
      if len(files) < 2:
        continue
      
      for filename in sorted(files):
        dupes_csv.writerow({'Group': group, 'File': filename})
  
  def files_in_group(self, group):
    
    if not group in self.dupes:
      return None
    else:
      return self.dupes[group]
  
  def group_from_file(self, filename):
    
    filename = dir_tools.normalize(filename)
    
    for group in self.dupes:
      if filename in self.dupes[group]:
        return group
    
    return None
  
  def files_in_same_group(self, filename):
    
    group = self.group_from_file(filename)
    
    if not group == None:
      return self.files_in_group(group)
    
    return None
  
  def is_file_in_group(self, filename, group):
    filename = dir_tools.normalize(filename)
    return filename in self.dupes[group]

  ################################################################################
  ### @fn   add_file(file, group)
  ### @desc Adds the file to the given group. If group == None, a new group is
  ###       created.
  ### @retn Returns the group the file was added to, or None if not.
  ################################################################################
  def add_file(self, filename, group = None):
    filename = dir_tools.normalize(filename)
    
    test_group = self.group_from_file(filename)
    if not test_group == None:
      _LOGGER.error("File %s already a member of group %d. Try merging groups." % (filename, test_group))
      return None
    
    if group == None:
      group = max(self.dupes.keys()) + 1
    
    self.dupes[group].add(filename)
    
    return group

  def remove_file(self, filename):
    filename = dir_tools.normalize(filename)
    
    group = self.group_from_file(filename)
    if group == None:
      _LOGGER.error("File %s not in any duplicate group, cannot remove." % filename)
      return
    
    # If we have two or fewer and attempt to remove a file,
    # that would leave us with a group with one file, which
    # isn't much of a duplicate group. So just save the trouble
    # and kill it all right here.
    if len(self.dupes[group]) <= 2:
      self.remove_group(group)
    else:
      self.dupes[group].discard(filename)

  def remove_group(self, group):
    if not group in self.dupes:
      _LOGGER.error("Cannot remove group %d. Group does not exist." % group)
      return
    
    del self.dupes[group]
    
  def merge_groups(self, groups):
    groups = set(groups)
    if len(groups) < 2:
      return
    
    new_group = min(groups)
    groups.remove(new_group)
    
    self.dupes[new_group].update(*[self.dupes[group] for group in groups])
    
    for group in groups:
      del self.dupes[group]

################################################################################
### MAIN
################################################################################

db = DupesDB()

# if __name__ == "__main__":

  # import pprint
  # import time
  # import glob
  # pp = pprint.PrettyPrinter()
  
  # gfx_db = DupesDB("data/dupes-models-pruned.csv")
  
  # for i in xrange(1000):
    # files = gfx_db.files_in_group(i)
    # if files == None:
      # continue
    
    # for file in files:
      # temp = db.group_from_file(file)
      
      # if temp == None:
        # continue
      
      # db.remove_file(file)
    
    # group = None
    # for file in files:
      # group = db.add_file(file, group)
      
      # if group == None:
        # print "Failed to add %s" % file
    
  # db.save_csv()

### EOF ###