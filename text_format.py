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

from enum import Enum
import common

TEXT_ALIGN   = Enum("left", "right", "center", "offcenter")
TEXT_ORIENT  = Enum("hor", "ver")

class TextFormat:
  def __init__(self, x = 0, y = 0, w = 480, h = 24, align = TEXT_ALIGN.left,
               orient = TEXT_ORIENT.hor, clt = 0, kill_blanks = False):
    
    self.x            = x
    self.y            = y
    self.w            = w
    self.h            = h
    self.align        = align
    self.orient       = orient
    self.clt          = clt
    self.kill_blanks  = kill_blanks

TEXT_FORMATS = {
  None:                           TextFormat(),
  common.SCENE_MODES.normal:      TextFormat(x =  46, y = 216, w = 444, h = 24, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt =  0, kill_blanks = True),
  common.SCENE_MODES.normal_flat: TextFormat(x =  18, y = 208, w = 444, h = 27, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt =  0, kill_blanks = True),
  common.SCENE_MODES.trial:       TextFormat(x =  18, y = 207, w = 444, h = 27, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt =  0, kill_blanks = True),
  common.SCENE_MODES.rules:       TextFormat(x =  32, y = 165, w = 416, h = 18, align = TEXT_ALIGN.center,  orient = TEXT_ORIENT.hor, clt =  0, kill_blanks = True),
  common.SCENE_MODES.ammo:        TextFormat(x =  50, y =  88, w = 185, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = False),
  common.SCENE_MODES.ammoname:    TextFormat(x =  36, y =  50, w = 200, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = True),
  common.SCENE_MODES.ammosummary: TextFormat(x =  41, y = 198, w = 200, h = 12, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = False),
  common.SCENE_MODES.present:     TextFormat(x =  50, y =  88, w = 185, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = False),
  common.SCENE_MODES.presentname: TextFormat(x =  66, y =  50, w = 200, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = True),
  common.SCENE_MODES.debate:      TextFormat(x =   0, y = 160, w = 480, h = 24, align = TEXT_ALIGN.center,  orient = TEXT_ORIENT.hor, clt = 16, kill_blanks = True),
  common.SCENE_MODES.mtb:         TextFormat(x =  18, y = 160, w = 444, h = 24, align = TEXT_ALIGN.center,  orient = TEXT_ORIENT.hor, clt =  2, kill_blanks = True),
  common.SCENE_MODES.climax:      TextFormat(x =  18, y = 208, w = 444, h = 27, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt =  0, kill_blanks = True),
  common.SCENE_MODES.anagram:     TextFormat(x =  18, y = 202, w = 420, h = 24, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 16, kill_blanks = True),
  common.SCENE_MODES.menu:        TextFormat(x =  55, y = 204, w = 370, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = True),
  common.SCENE_MODES.map:         TextFormat(x =  38, y =  65, w = 200, h = 14, align = TEXT_ALIGN.center,  orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = True),
  common.SCENE_MODES.report:      TextFormat(x = 170, y =  90, w = 292, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = True),
  common.SCENE_MODES.report2:     TextFormat(x = 182, y = 187, w = 292, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = True),
  common.SCENE_MODES.skill:       TextFormat(x =  18, y = 106, w = 292, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = False),
  common.SCENE_MODES.skill2:      TextFormat(x = 248, y = 154, w = 292, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = True),
  common.SCENE_MODES.music:       TextFormat(x =  95, y = 112, w = 180, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = True),
  common.SCENE_MODES.eventname:   TextFormat(x =  29, y =  59, w = 196, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 89, kill_blanks = True),
  common.SCENE_MODES.artworkname: TextFormat(x =  29, y =  59, w = 196, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 89, kill_blanks = True),
  common.SCENE_MODES.moviename:   TextFormat(x =  29, y =  59, w = 196, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 89, kill_blanks = True),
  common.SCENE_MODES.theatre:     TextFormat(x =  18, y = 208, w = 444, h = 27, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt =  0, kill_blanks = True),
  common.SCENE_MODES.help:        TextFormat(x =  34, y =  24, w = 420, h = 20, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = False),
  common.SCENE_MODES.other:       TextFormat(x =  18, y =  24, w = 420, h = 14, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt = 90, kill_blanks = False),
  common.SCENE_MODES.novel:       TextFormat(x =  28, y =  25, w = 420, h = 20, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt =  0, kill_blanks = False),
  common.SCENE_SPECIAL.option:    TextFormat(x = 200, y = 143, w = 254, h = 25, align = TEXT_ALIGN.left,    orient = TEXT_ORIENT.hor, clt =  0, kill_blanks = True),
}

### EOF ###