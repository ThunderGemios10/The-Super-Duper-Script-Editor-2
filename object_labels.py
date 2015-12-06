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

import os, codecs
from list_files import list_all_files
from script_file import ScriptFile

import common

def get_label(id, dir):
  if not isinstance(id, int):
    return None
  
  filename = os.path.join(dir, "%04d.txt" % id)
  
  if not os.path.isfile(filename):
    return None
  
  line = ScriptFile(filename)
  
  label = line[common.editor_config.lang_trans]
  if label == "":
    label = line[common.editor_config.lang_orig]
  
  if label == u"※" or label == "":
    return None
  
  label = label.strip()
  
  return label

def get_obj_label(map_id, obj_id, data_dir = common.editor_config.data01_dir):
  dir = os.path.join(data_dir, "jp", "script", "MAP_%03d.pak" % map_id)
  return get_label(obj_id, dir)

def get_char_name(char_id, data_dir = common.editor_config.data01_dir):
  dir = os.path.join(data_dir, "jp", "script", "32_CharaName.pak")
  return get_label(char_id, dir)

def get_map_name(map_id, data_dir = common.editor_config.data01_dir):
  dir = os.path.join(data_dir, "jp", "script", "18_MapName.pak")
  return get_label(map_id, dir)

def get_bgm_name(bgm_id, data_dir = common.editor_config.data01_dir):
  dir = os.path.join(data_dir, "jp", "script", "34_BgmNameEnglish.pak")
  return get_label(bgm_id, dir)

def get_ammo_name(ammo_id, data_dir = common.editor_config.data01_dir):
  dir = os.path.join(data_dir, "jp", "script", "06_KotodamaName.pak")
  return get_label(ammo_id, dir)

def get_present_name(present_id, data_dir = common.editor_config.data01_dir):
  dir = os.path.join(data_dir, "jp", "script", "04_ItemName.pak")
  return get_label(present_id, dir)


### EOF ###