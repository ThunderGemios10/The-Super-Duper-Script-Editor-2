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

FONT1 = 1
FONT2 = 2

class FontSettings():
  def __init__(self, font_data = None, gen_for_game = True,
      gen_for_editor = True, font_type = FONT1, left_to_right = True):
    
    if not font_data:
      self.font_data = []
    else:
      self.font_data = font_data
    
    self.gen_for_game   = gen_for_game
    self.gen_for_editor = gen_for_editor
    self.font_type      = font_type
    self.left_to_right  = left_to_right

### EOF ###