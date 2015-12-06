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

from scene_info import SceneInfo
from collections import defaultdict

# Kind of imitating the ScriptFile class.
class ScriptJump(object):
  
  def __init__(self, scene_info):
    self.scene_info = scene_info
    
    self.ch     = scene_info.goto_ch
    self.scene  = scene_info.goto_scene
    self.room   = scene_info.goto_room
    
    self.text     = u""
    self.notags   = defaultdict(lambda: u"")
    self.comments = u""
    self.filename = u"→ " + self.target()
  
  def target(self):
    return u"e%02d_%03d_%03d.lin" % (self.ch, self.scene, self.room)
      
  def __getitem__(self, lang):
    return u""
  
  def __setitem__(self, lang, text):
    pass

### EOF ###