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

import os

import common
from enum import Enum

SPRITE_TYPE = Enum("bustup", "stand")

class SpriteId():
  def __init__(
    self,
    sprite_type = SPRITE_TYPE.bustup,
    char_id = -1,
    sprite_id = -1
  ):
    self.sprite_type = sprite_type
    self.char_id = char_id
    self.sprite_id = sprite_id

def get_sprite_file(sprite_id):
  
  if sprite_id.char_id == -1 or sprite_id.sprite_id == -1:
    return None
  
  filename = "%s_%02d_%02d.png" % (str(sprite_id.sprite_type), sprite_id.char_id, sprite_id.sprite_id)
  return filename

### EOF ###