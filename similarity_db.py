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

import os.path
import sqlite3
import threading
import time
from collections import deque

import common
import dir_tools

_CACHE_SIZE = 1000

class SimilarityDB:
  def __init__(self):
    self.__similarities = {}
    self.__accessed     = [[None, False]] * _CACHE_SIZE
    self.__cache_frame  = 0
    
    self.__threshold    = common.editor_config.similarity_thresh
    
    self.__queue = deque([])
    
    self.__queue_lock = threading.Lock()
    self.__similarities_lock = threading.Lock()
    self.__db_lock = threading.Lock()
    
    self.__thread = threading.Thread(target = self.__process_queue)
    # Do not allow this thread to prevent the program from closing
    # since I'm a retard and haven't come up with a decent way to
    # kill the thread when the main window is closed.
    self.__thread.daemon = True
    
    self.__conn = sqlite3.connect(common.editor_config.similarity_db, check_same_thread = False)
    self.__conn.row_factory = sqlite3.Row
    self.__c = self.__conn.cursor()
    
    self.__running = True
    
    self.__thread.start()
  
  def __del__(self):
    self.__c.close()
    self.__running = False
  
  def __process_queue(self):
    
    while True:
      if self.__running == False:
        break
      
      self.__queue_lock.acquire()
      if len(self.__queue) == 0:
        self.__queue_lock.release()
        time.sleep(0.1)
        continue
      # self.__queue_lock.release()
      
      # self.__queue_lock.acquire()
      queued = self.__queue.pop()
      self.__queue_lock.release()
      
      #####
      self.__similarities_lock.acquire()
      if queued in self.__similarities:
        self.__similarities_lock.release()
        continue
      self.__similarities_lock.release()
      
      sim = self.__find_similar(queued)
      
      # self.__similarities_lock.acquire()
      # self.__similarities[queued] = sim
      # self.__similarities_lock.release()
      self.__store_similarities(queued, sim)
      #####
  
  def __find_similar(self, filename):
  
    filename = dir_tools.normalize(filename)
    
    #####
    self.__db_lock.acquire()
    
    self.__c.execute('''SELECT * FROM similarity
                        WHERE (file1 = ? OR file2 = ?)
                        AND (percent >= ?)''',
                  (filename, filename, self.__threshold))
    
    sim = []
    
    for row in self.__c:
      file = row['file1']
      if file == filename:
        file = row['file2']
      
      sim.append(file)
        
    self.__db_lock.release()
    #####
    
    return sim
  
  def __store_similarities(self, filename, similarities):
    filename = dir_tools.normalize(filename)
    
    #####
    self.__similarities_lock.acquire()
    
    while self.__accessed[self.__cache_frame][1] == True:
      self.__accessed[self.__cache_frame][1] = False
      self.__cache_frame += 1
      
      if self.__cache_frame >= _CACHE_SIZE:
        self.__cache_frame = 0
    
    old_name = self.__accessed[self.__cache_frame][0]
    try:
      del self.__similarities[old_name]
    except:
      pass
    
    self.__similarities[filename] = similarities
    self.__accessed[self.__cache_frame] = [filename, True]
    
    self.__similarities_lock.release()
    #####
  
  def __get_similarities(self, filename):
    filename = dir_tools.normalize(filename)
  
    #####
    self.__similarities_lock.acquire()
    
    if filename in self.__similarities:
      sim = self.__similarities[filename]
      
      for i, (name, accessed) in enumerate(self.__accessed):
        if name == filename:
          self.__accessed[i][1] = True
          break
      
      self.__similarities_lock.release()
      return sim
      
    self.__similarities_lock.release()
    #####
    
    sim = self.__find_similar(filename)
    self.__store_similarities(filename, sim)
    
    return sim
  
  def get_similarities(self, filename):
    return self.__get_similarities(filename)
  
  def add_similar(self, file1, file2, percent = 100):
    self.add_similar_files([file1], [file2], percent)
  
  def add_similar_files(self, file_list1, file_list2, percent):
    
    self.__db_lock.acquire()
    self.__similarities_lock.acquire()
    
    for file1 in file_list1:
      file1 = dir_tools.normalize(file1)
      
      for file2 in file_list2:
        file2 = dir_tools.normalize(file2)
        
        if file1 == file2:
          continue
        
        self.__c.execute('''SELECT * FROM similarity
                          WHERE ((file1 = ? AND file2 = ?)
                          OR (file1 = ? AND file2 = ?))
                       ''', (file2, file1, file1, file2))
        # Only add if we don't have the entry normal or reversed.
        if self.__c.fetchone() == None:
          self.__c.execute('''INSERT OR IGNORE INTO similarity
                            VALUES(?, ?, ?)
                         ''', (file1, file2, percent))
        
        # Make sure we have up-to-date info.
        if file1 in self.__similarities:
          del self.__similarities[file1]
        
        if file2 in self.__similarities:
          del self.__similarities[file2]
        
        #self.__queue_query_at_top(file1)
        #self.__queue_query_at_top(file2)
    
    self.__conn.commit()
    
    self.__similarities_lock.release()
    self.__db_lock.release()
  
  def remove_similar(self, file1, file2):
    self.remove_similar_files([file1], [file2])
  
  def remove_similar_files(self, file_list1, file_list2):
    
    if file_list1 == None or len(file_list1) == 0 or file_list2 == None or len(file_list2) == 0:
      return
    
    self.__db_lock.acquire()
    self.__similarities_lock.acquire()
    
    for file1 in file_list1:
    
      file1 = dir_tools.normalize(file1)
      
      # Make sure we have up-to-date info.
      if file1 in self.__similarities:
        del self.__similarities[file1]
      #self.__queue_query_at_top(file1)
      
      for file2 in file_list2:
        file2 = dir_tools.normalize(file2)
      
        self.__c.execute('''DELETE FROM similarity
                          WHERE ((file1 = ? AND file2 = ?)
                          OR (file1 = ? AND file2 = ?))
                       ''', (file2, file1, file1, file2))
        
        if file2 in self.__similarities:
          del self.__similarities[file2]
        #self.__queue_query_at_top(file2)
    
    self.__conn.commit()
    
    self.__similarities_lock.release()
    self.__db_lock.release()
  
  def queue_query(self, filename):
    
    self.__queue_lock.acquire()
    self.__queue.appendleft(filename)
    self.__queue_lock.release()
  
  def queue_query_at_top(self, filename):
    
    self.__queue_lock.acquire()
    self.__queue.append(filename)
    self.__queue_lock.release()
  
  def clear_queue(self):
    
    self.__queue_lock.acquire()
    self.__queue = deque([])
    self.__queue_lock.release()
  
  def clear(self):
    #self.__thread.pause()
    
    self.clear_queue()
    
    self.__similarities_lock.acquire()
    self.__similarities = {}
    self.__accessed     = [[None, False]] * _CACHE_SIZE
    self.__cache_frame  = 0
    self.__similarities_lock.release()
    
    #self.__thread.start()

### EOF ###