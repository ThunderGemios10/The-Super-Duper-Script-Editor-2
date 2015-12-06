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
import re

from PyQt4 import QtCore
from PyQt4.QtCore import QString

from config import EditorConfig
from enum import Enum

SCENE_MODES   = Enum("normal", "normal_flat", "trial", "rules", "ammo", "ammoname", "ammosummary", "present", "presentname", "debate", "mtb", "climax", "anagram", "dive", "hanron", "menu", "map", "report", "report2", "skill", "skill2", "music", "eventname", "artworkname", "moviename", "theatre", "novel", "help", "other")
SCENE_SPECIAL = Enum("option", "showopt", "react", "debate", "chatter", "hanron", "checkobj", "checkchar")
BOX_COLORS    = Enum("yellow", "green", "blue")
BOX_TYPES     = Enum("normal", "flat", "novel")

CHAPTER_MONOKUMA = 100
CHAPTER_FREETIME = 101
CHAPTER_ISLAND   = 102
CHAPTER_NOVEL    = 103

editor_config     = EditorConfig()

LOGGER_NAME = "sdse"
logging.getLogger(LOGGER_NAME).setLevel(editor_config.log_level.upper())

RE_DIRNAME = re.compile(ur".*?e(?P<chapter>\d\d)_(?P<scene>\d\d\d)_(?P<room>\d\d\d)\.lin", re.I)
RE_SYSDIR  = re.compile(ur"(?P<index>\d\d)_(?P<name>.*?)\.pak", re.I)

COURTROOM_ID = 200

def get_dir_info(directory):

  dir_info = RE_DIRNAME.match(directory)
  sys_info = RE_SYSDIR.match(directory)
  
  chapter = -1
  scene = -1
  room = -1
  mode = SCENE_MODES.other
  
  if not dir_info == None:
    chapter, scene, room = dir_info.group("chapter", "scene", "room")
    chapter = int(chapter)
    scene = int(scene)
    room = int(room)
    
    # Misc text.
    if chapter == 8:
      
      if scene == 100:
        mode = SCENE_MODES.theatre
        chapter = CHAPTER_MONOKUMA
        # Because the "room" portion of the directory name actually distinguishes
        # between different Monokuma Theatre events, so it makes more sense to
        # refer to that as the "scene" than the "room"
        scene = room
        room = 0
      
      elif scene >= 1 and scene <= 15:
        mode = SCENE_MODES.normal
        chapter = CHAPTER_FREETIME
        # scene = 0
        room = 0
      
      else:
        mode = SCENE_MODES.normal
        chapter = -1
        scene = 0
        room = 0
    
    elif chapter == 9:
      mode = SCENE_MODES.normal
      chapter = CHAPTER_ISLAND
      
      if scene >= 701 and scene <= 715:
        if room == 101:
          scene = -1
          mode = SCENE_MODES.debate
        
      room = 0
    
    else:
    
      if scene >= 200 and scene < 300:
        if room == 0:
          mode = SCENE_MODES.trial
        elif room == 1:
          mode = SCENE_MODES.debate
        room = 216 + chapter # Courtroom, lol
        
      elif scene == 999:
        mode = SCENE_MODES.normal
        room = 0
        
      else:
        mode = SCENE_MODES.normal
  
  elif not sys_info == None:
  
    index, name = sys_info.group("index", "name")
    name = name.lower()
    
    chapter = -1
    scene = -1
    room = -1
    
    if name in ["kotodamadesc1", "kotodamadesc2", "kotodamadesc3"]:
      mode = SCENE_MODES.ammo
      
    elif name == "kotodamaname":
      mode = SCENE_MODES.ammoname
    
    elif name == "itemdescription":
      mode = SCENE_MODES.present
      
    elif name == "itemname":
      mode = SCENE_MODES.presentname
    
    elif name == "rule":
      mode = SCENE_MODES.rules
    
    elif name == "report":
      mode = SCENE_MODES.report
    
    elif name in ["special", "skilldeschb", "profile"]:
      mode = SCENE_MODES.report2
    
    elif name == "skilldesc":
      mode = SCENE_MODES.skill
    
    elif name == "skillname":
      mode = SCENE_MODES.skill2
    
    elif name in ["floorname", "mapname"]:
      mode = SCENE_MODES.map
    
    elif name in ["eventname"]:
      mode = SCENE_MODES.eventname
    
    elif name in ["artworkname"]:
      mode = SCENE_MODES.artworkname
    
    elif name == "moviename":
      mode = SCENE_MODES.moviename
    
    elif name == "bgmname":
      mode = SCENE_MODES.music
    
    elif name == "operatesysr":
      mode = SCENE_MODES.help
    
    elif name in ["system", "contents", "briefing", "credit", "anagram", "charaname", "mapnameenglish", "bgmnameenglish", "pet", "survivaltitle"]:
      mode = SCENE_MODES.other
    
    elif name in ["operatemode", "operatedesc", "handbookmenu", "handbookdesc", "menu", "operatemoder", "operatedescr", "option", "skillexchange"]:
      mode = SCENE_MODES.menu
    
    else:
      mode = SCENE_MODES.other
  
  elif directory[:5] == "mtb_s":
    chapter = -1
    scene = -1
    room = COURTROOM_ID
    mode = SCENE_MODES.mtb
  
  elif directory[:6] == "mtb2_s" or directory[:10] == "dr2_mtb2_s":
    chapter = -1
    scene = -1
    room = COURTROOM_ID
    mode = SCENE_MODES.mtb
    
  elif directory[:7] == "anagram":
    chapter = -1
    scene = -1
    room = COURTROOM_ID
    mode = SCENE_MODES.anagram
  
  elif directory[:7] == "nonstop":
    chapter = -1
    scene = -1
    room = COURTROOM_ID
    mode = SCENE_MODES.debate
  
  elif directory[:6] == "hanron":
    chapter = -1
    scene = -1
    room = COURTROOM_ID
    mode = SCENE_MODES.hanron
  
  elif directory[:6] == "kokoro":
    chapter = CHAPTER_ISLAND
    scene = -1
    room = 0
    mode = SCENE_MODES.debate
  
  elif directory[:11] == "logicaldive":
    chapter = -1
    scene = -1
    room = COURTROOM_ID
    mode = SCENE_MODES.dive
  
  elif directory[:5] == "novel":
    chapter = CHAPTER_NOVEL
    scene   = int(directory[6:9])
    room    = -1
    mode    = SCENE_MODES.novel
  
  elif directory[:3] == "MAP":
    chapter = -1
    scene   = -1
    room    = int(directory[4:7])
    mode = SCENE_MODES.map
  
  elif directory[:10] == "script_pak":
    chapter = -1
    scene = -1
    room = 0
    mode = SCENE_MODES.normal
  
  return chapter, scene, room, mode

def mode_to_text(scene_mode):
  
  text = u""
  
  if scene_mode == SCENE_MODES.normal:
    text = u"Normal"
  elif scene_mode == SCENE_MODES.trial:
    text = u"Class Trial"
  elif scene_mode == SCENE_MODES.rules:
    text = u"Rules"
  elif scene_mode in [SCENE_MODES.ammo, SCENE_MODES.ammoname, SCENE_MODES.present, SCENE_MODES.presentname]:
    text = u"Ammunition/Presents"
  elif scene_mode == SCENE_MODES.debate:
    text = u"Nonstop Debate"
  elif scene_mode == SCENE_MODES.mtb:
    text = u"Machinegun Talk Battle"
  elif scene_mode == SCENE_MODES.climax:
    text = u"Climax Logic"
  elif scene_mode == SCENE_MODES.anagram:
    text = u"Epiphany Anagram"
  elif scene_mode == SCENE_MODES.menu:
    text = u"Menu"
  elif scene_mode == SCENE_MODES.map:
    text = u"Room/Item Names"
  elif scene_mode == SCENE_MODES.report or scene_mode == SCENE_MODES.report2:
    text = u"Report Cards"
  elif scene_mode == SCENE_MODES.skill or scene_mode == SCENE_MODES.skill2:
    text = u"Skills"
  elif scene_mode == SCENE_MODES.music:
    text = u"Sound Test"
  elif scene_mode == SCENE_MODES.eventname or scene_mode == SCENE_MODES.moviename:
    text = u"Event/Movie Gallery"
  elif scene_mode == SCENE_MODES.help:
    text = u"Help"
  elif scene_mode == SCENE_MODES.novel:
    text = u"Omake VN"
  elif scene_mode == SCENE_MODES.other:
    text = u"Other"
  else:
    text = u"N/A"
  
  return text
  
def chapter_to_text(chapter):

  text = ""
  
  if chapter == 0:
    text = u"Prologue"
  elif chapter >= 1 and chapter <= 6:
    text = u"Chapter %d" % chapter
  elif chapter == 7:
    text = u"Epilogue"
  elif chapter == CHAPTER_MONOKUMA:
    text = u"Monokuma Theatre"
    #text = u"モノクマ劇場"
    #text = u"M. Theatre"
  elif chapter == CHAPTER_FREETIME:
    text = u"Free Time"
  elif chapter == CHAPTER_ISLAND:
    text = u"Dangan☆Island"
  elif chapter == CHAPTER_NOVEL:
    text = u"Omake VN"
  elif chapter == -1 or chapter == None:
    text = u"N/A"
  else:
    text = u"Other"
  
  return text

def qt_to_unicode(str, normalize = True):
  if normalize:
    str = str.normalized(QString.NormalizationForm_C)
  
  return unicode(str.toUtf8(), "UTF-8")

### EOF ###