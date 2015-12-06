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

from PyQt4 import QtGui, QtCore

import os
import re
from types import *

import common
from make_unique import make_unique

################################################################################
### @fn   list_to_tree()
### @desc Converts the awkward list format from script_map to a nicer tree.
################################################################################
def list_to_tree(data):
  
  tree_items = []
  
  for item in data:
    
    tree_items.append(QtGui.QTreeWidgetItem())
    
    if type(item) == TupleType:
      item_name     = item[0]
      item_children = item[1]
      
      tree_items[-1].setText(0, item_name)
      
      children = list_to_tree(item_children)
      
      for child in children:
        tree_items[-1].addChild(child)
    
    else:
      tree_items[-1].setText(0, item)
    
  return tree_items

def path_to_tree(filename):
  
  tree_item = None
  child = QtGui.QTreeWidgetItem()
  
  filename = os.path.normpath(filename)
  
  # Kill leading slashes, because we hate them.
  filename = re.sub("^[\\\/]*", "", filename)
  
  while True:
    filename, tail = os.path.split(filename)
    
    if tail == "":
      continue
    
    child.setText(0, tail)
    
    if filename == "" or filename == "/" or filename == "\\":
      tree_item = child
      break
    
    tree_item = QtGui.QTreeWidgetItem()
    tree_item.addChild(child)
    child = tree_item
  
  return tree_item

def tree_item_to_path(tree_item):
  
  if tree_item == None:
    return ""
  
  path = common.qt_to_unicode(tree_item.text(0))
  tree_item = tree_item.parent()
  
  while tree_item != None:
    base = common.qt_to_unicode(tree_item.text(0))
    path = os.path.join(base, path)
    tree_item = tree_item.parent()
  
  return path

def consolidate_tree_items(tree_items):
  
  if len(tree_items) == 0:
    return tree_items
  
  headers = []
  item_map = {}
  
  for item in tree_items:
    header = common.qt_to_unicode(item.text(0))
    headers.append(header)
    
    if not header in item_map:
      item_map[header] = []
    
    item_map[header].append(item)
  
  # We only want one of each header.
  headers = make_unique(headers)
  headers.sort()
  
  new_tree_items = []
  
  for header in headers:
    tree_item = QtGui.QTreeWidgetItem()
    tree_item.setText(0, header)
    
    children = []
    for item in item_map[header]:
      for index in range(item.childCount()):
        children.append(item.child(index))
    
    children = consolidate_tree_items(children)
    
    for child in children:
      tree_item.addChild(child)
    
    new_tree_items.append(tree_item)
  
  return new_tree_items