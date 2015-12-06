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
import re
import time

try:
  import cPickle as pickle
except:
  import pickle

import common
import list_files
from script_file import ScriptFile
from script_pack import SCRIPT_DIR

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

DATA_FILE = "data/analytics.bin"
DEFAULT_FILTER = re.compile(ur"\d\d_.*\.pak|e\d\d|event\.pak|ldive_s\d\d\.pak|MAP_\d\d\d\.pak|mtb2?_s\d\d\.pak|novel_\d\d\d\.lin|script_pak|voice\.pak", re.IGNORECASE | re.DOTALL | re.UNICODE)

SEARCH_ORIGINAL       = 0b0001
SEARCH_TRANSLATED     = 0b0010
SEARCH_COMMENTS       = 0b0100
SEARCH_NOTAGS         = 0b1000
DEFAULT_SEARCH_FLAGS  = SEARCH_ORIGINAL | SEARCH_TRANSLATED | SEARCH_COMMENTS

MIN_INTERVAL          = 0.100

################################################################################
### @class ScriptData
################################################################################
class ScriptData():

  ####################################################################
  ### @fn __init__()
  ####################################################################
  def __init__(self, filename = None):
    self.filesize = None
    self.last_edited = None
    self.data = None
    
    if filename:
      self.load_file(filename)
  
  ####################################################################
  ### @fn load_file(filename)
  ####################################################################
  def load_file(self, filename):
    if not os.path.isfile(filename):
      return
    
    stats = os.stat(filename)
    data = ScriptFile(filename)
    
    self.filesize     = int(stats.st_size)
    self.last_edited  = int(stats.st_mtime)
    self.data         = data
    
  ####################################################################
  ### @fn update()
  ####################################################################
  def update(self):
    if not self.needs_update():
      return
    
    self.load_file(self.data.filename)
  
  ####################################################################
  ### @fn needs_update()
  ####################################################################
  def needs_update(self):
    if not isinstance(self.data, ScriptFile):
      _LOGGER.warning("Probably shouldn't be doing this.")
      return True
    
    try:
      stats = os.stat(self.data.filename)
    except:
      return True
    
    filesize    = int(stats.st_size)
    last_edited = int(stats.st_mtime)
    
    return not (filesize == self.filesize and last_edited == self.last_edited)

################################################################################
### @class ScriptAnalytics
################################################################################
class ScriptAnalytics():

  ####################################################################
  ### @fn __init__()
  ####################################################################
  def __init__(self):
    self.script_data = {}
    self.load()
  
  ####################################################################
  ### @fn load()
  ####################################################################
  def load(self):
    try:
      with open(DATA_FILE, "rb") as f:
        self.script_data = pickle.load(f)
    except:
      self.script_data = {}
    self.quick_update()
  
  ####################################################################
  ### @fn save()
  ####################################################################
  def save(self):
    with open(DATA_FILE, "wb") as f:
      pickle.dump(self.script_data, f, pickle.HIGHEST_PROTOCOL)
  
  ####################################################################
  ### @fn update(dir_filter)
  ### Updates files whose directory match the filter.
  ####################################################################
  def update(self, dir_filter = DEFAULT_FILTER):
    for txt_file in ScriptAnalytics.list_txt_files(dir_filter):
      self.update_file(txt_file)
  
  ####################################################################
  ### @fn quick_update(dir_filter)
  ### Does a quick update only on files that don't exist.
  ####################################################################
  def quick_update(self, dir_filter = DEFAULT_FILTER):
    for txt_file in ScriptAnalytics.list_txt_files(dir_filter):
      if txt_file in self.script_data:
        continue
      self.update_file(txt_file)
  
  ####################################################################
  ### @fn update_file(filename)
  ### Updates the given file.
  ####################################################################
  def update_file(self, filename):
    try:
      self.script_data[filename].update()
    except:
      self.script_data[filename] = ScriptData(os.path.join(common.editor_config.data01_dir, filename))
      #print "Probably shouldn't be doing this."
  
  ####################################################################
  ### @fn search_gen(text_filter, dir_filter, search_flags)
  ### Returns a list of files whose contents match the text filter
  ### and whose directory matches the directory filter.
  ### This is a generator which yields:
  ###  * the current file number
  ###  * the total number of files
  ###  * the current filename
  ###  * a list of matches found since the last yield
  ####################################################################
  def search_gen(self, text_filter, dir_filter = DEFAULT_FILTER, search_flags = DEFAULT_SEARCH_FLAGS):
    matches = []
    
    original    = search_flags & SEARCH_ORIGINAL
    translated  = search_flags & SEARCH_TRANSLATED
    comments    = search_flags & SEARCH_COMMENTS
    notags      = search_flags & SEARCH_NOTAGS
    
    last_update = time.time()
    
    for i, path in enumerate(self.script_data):
    # for i, path in enumerate(ScriptAnalytics.list_txt_files(dir_filter)):
      if time.time() - last_update > MIN_INTERVAL:
        yield i, len(self.script_data), path, matches
        matches = []
        last_update = time.time()
      
      if not dir_filter.search(path):
        continue
      
      self.update_file(path)
      data = self.script_data[path]
      
      to_search = []
      if original:
        to_search.append(data.data.notags[common.editor_config.lang_orig] if notags else data.data[common.editor_config.lang_orig])
        
      if translated:
        to_search.append(data.data.notags[common.editor_config.lang_trans] if notags else data.data[common.editor_config.lang_trans])
        
      if comments:
        to_search.append(data.data.comments)
      
      # to_search = "\n".join(to_search)
      
      # if text_filter.search(to_search):
        # matches.append(path)
      for line in to_search:
        if text_filter.search(line):
          matches.append(path)
          break
    
    yield len(self.script_data), len(self.script_data), "", matches
  
  ####################################################################
  ### @fn search(text_filter, dir_filter, search_flags)
  ### Returns a list of files whose contents match the text filter
  ### and whose directory matches the directory filter.
  ####################################################################
  def search(self, text_filter, dir_filter = DEFAULT_FILTER, search_flags = DEFAULT_SEARCH_FLAGS):
    matches = []
    
    for index, total, path, cur_matches in search_gen(text_filter, dir_filter, search_flags):
      matches.extend(cur_matches)
    
    return matches
  
  ####################################################################
  ### @fn get_data(dir_filter)
  ### A generator which yields:
  ###  * the file number
  ###  * the total number of files
  ###  * the filename
  ###  * and the data field of each file that matches the filter
  ###    or None if there wasn't a match at a periodic interval
  ####################################################################
  def get_data(self, dir_filter = DEFAULT_FILTER):
    last_update = time.time()
    
    for i, path in enumerate(sorted(self.script_data.keys())):
    # for i, path in enumerate(ScriptAnalytics.list_txt_files(dir_filter)):
      if not dir_filter.search(path):
        if time.time() - last_update > MIN_INTERVAL:
          yield i, len(self.script_data), path, None
          last_update = time.time()
          
        continue
      
      self.update_file(path)
      data = self.script_data[path]
      
      yield i, len(self.script_data), path, data.data
      last_update = time.time()
  
  ####################################################################
  ### @fn list_txt_files(dir_filter)
  ### Returns a list of files whose directory match the filter.
  ####################################################################
  @staticmethod
  def list_txt_files(dir_filter = DEFAULT_FILTER):
  
    # For our dupe database, we need the relative location of our files, not absolute.
    dir_start = len(common.editor_config.data01_dir) + 1
    
    for dir in ScriptAnalytics.list_dirs(dir_filter):
      dir_files = list_files.list_all_files(os.path.join(common.editor_config.data01_dir, SCRIPT_DIR, dir))
      for file in dir_files:
        if os.path.splitext(file)[1].lower() == ".txt":
          yield file[dir_start:]
  
  ####################################################################
  ### @fn list_dirs(filter)
  ### Returns a list of directories that match the filter.
  ####################################################################
  @staticmethod
  def list_dirs(filter = DEFAULT_FILTER):
    
    base_dir = os.path.join(common.editor_config.data01_dir, SCRIPT_DIR)
    for item in os.listdir(base_dir):
      full_path = os.path.join(base_dir, item)
      
      if os.path.isdir(full_path):
        if filter.search(item):
          yield item

SA = ScriptAnalytics()

if __name__ == "__main__":
  
  import sys
  handler = logging.StreamHandler(sys.stdout)
  # logging.getLogger(common.LOGGER_NAME).addHandler(handler)

  start_time = None
  def lazy_timer():
    global start_time
    if start_time == None:
      start_time = time.time()
    else:
      old_start = start_time
      start_time = time.time()
      elapsed = start_time - old_start
      print elapsed, "seconds since last call"
  lazy_timer()
  
  # DATA_FILE = "data/analytics-test.bin"
  # analytics = ScriptAnalytics()
  # lazy_timer()
  
  #results = SA.search_gen(re.compile(ur"バカ", re.IGNORECASE | re.DOTALL | re.UNICODE))
  
  # results = []
  # for i, total, filename, partial_results in SA.search_gen(re.compile(ur"バカ", re.IGNORECASE | re.DOTALL | re.UNICODE)):
    # print i, total, filename, len(partial_results)
    # results.extend(partial_results)
  # print len(results)
  # lazy_timer()
  # analytics.save()
  # SA.save()
  # lazy_timer()
  
  # print SA.list_txt_files(re.compile(ur"e00_000"))
### EOF ###