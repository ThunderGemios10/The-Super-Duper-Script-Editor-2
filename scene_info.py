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

#from PyQt4 import QtGui
#from PyQt4.QtGui import QImage, QColor
from enum import Enum

#import text_printer
#from common import SCENE_MODES, SCENE_SPECIAL, BOX_COLORS
import common
from sprite import SpriteId
from text_format import TextFormat
from voice import VoiceId

class SceneInfo():
  def __init__(self,
               file_id    = -1,
               speaker    = -1,
               speaking   = False,
               sprite     = SpriteId(),
               voice      = VoiceId(),
               bgm        = -1,
               headshot   = -1,
               mode       = None,
               special    = None,
               format     = None,
               box_color  = common.BOX_COLORS.yellow,
               box_type   = common.BOX_TYPES.normal,
               ammo       = -1,
               present    = -1,
               bgd        = -1,
               cutin      = -1,
               flash      = -1,
               movie      = -1,
               img_filter = None,
               chapter    = -1,
               scene      = -1,
               room       = -1,
               extra_val  = -1,
               goto_ch    = -1,
               goto_scene = -1,
               goto_room  = -1,
              ):
    self.file_id    = file_id
    
    self.speaker    = speaker
    self.speaking   = speaking
    self.sprite     = sprite
    self.voice      = voice
    self.bgm        = bgm
    
    self.headshot   = headshot
    
    self.mode       = mode
    self.special    = special
    self.format     = format
    self.box_color  = box_color
    self.box_type   = box_type
    
    self.ammo       = ammo
    self.present    = present
    self.bgd        = bgd
    self.cutin      = cutin
    self.flash      = flash
    self.movie      = movie
    
    self.img_filter = img_filter
    
    self.chapter    = chapter
    self.scene      = scene
    self.room       = room
    
    self.extra_val  = extra_val

if __name__ == "__main__":
  from text_printer import draw_scene
  scene = SceneInfo(speaker = 0x18,
                    sprite = (2, 2),
                    mode = SCENE_MODES.trial,
                    room = 157,
                    chapter = 3,
                    speaking = True)
  bg = draw_scene(scene, "What do you think you're looking at?")
  #bg.save("temp.png")

### EOF ###