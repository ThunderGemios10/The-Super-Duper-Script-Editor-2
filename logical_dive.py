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

from PyQt4 import QtGui, Qt
from PyQt4.QtGui import QImage, QPainter, QColor

from bitstring import ConstBitStream, BitStream
import logging
import os

from enum import Enum

import common
from script_pack import ScriptPack
from text_printer import replace_all_colors

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

DIVE_DIR = os.path.join("all", "bin")

CLR_NORMAL    = QColor( 42, 255,  54, 255)
CLR_SPECIAL   = QColor(255, 255,  84, 255)
CLR_BOOSTER   = QColor(255, 255,   1, 255)
CLR_A1        = QColor(255,  53,  53, 255)
CLR_A2        = QColor(  1, 161, 255, 255)
CLR_A3        = QColor(255, 215,   1, 255)
CLR_PILLAR    = QColor( 80,  87, 255, 255)
CLR_RAMP      = QColor( 80,  87, 255, 255)
CLR_END       = QColor(255, 255, 255, 255)
CLR_UNKNOWN   = QColor(255, 255, 255, 255)
CLR_TRIGGER   = QColor(128, 128, 128, 255)
CLR_OBSTACLE  = QColor(255, 154,  27, 255)

BLOCK_W     = 128 / 4
BLOCK_H     = 128 / 4

ROW_LEN     = 12

class DiveParser():
  def __init__(self):
    self.filename = ""
    self.rows     = []
  
  def load(self, filename):
    
    self.filename = filename
    dive = ConstBitStream(filename = os.path.join(common.editor_config.data01_dir, DIVE_DIR, self.filename))
    
    # Header
    # XX XX XX XX -- ??? (Always 0x02)
    # XX XX XX XX -- Header length? (Always 0x10)
    # XX XX XX XX -- File size - header length
    # XX XX XX XX -- Padding?
    dive.read(32)
    header_len = dive.read("uintle:32")
    file_len   = dive.read("uintle:32")
    dive.read(32)
    
    num_rows = dive.read("uintle:32")
    
    for i in range(num_rows):
      offset = dive.read("uintle:32") + header_len
      row    = dive[offset * 8 : (offset + ROW_LEN) * 8].readlist("uint:8," * ROW_LEN)
      self.rows.append(row)
    
  def render_map(self):
    img_w = ROW_LEN * BLOCK_W
    img_h = len(self.rows) * BLOCK_H
    
    # Our base blocks
    base_booster  = QImage(os.path.join(common.editor_config.gfx_dir, "dive", "boost.png")).scaled(BLOCK_W, BLOCK_H, transformMode = Qt.Qt.SmoothTransformation)
    base_normal   = QImage(os.path.join(common.editor_config.gfx_dir, "dive", "normal.png")).scaled(BLOCK_W, BLOCK_H, transformMode = Qt.Qt.SmoothTransformation)
    base_slash    = QImage(os.path.join(common.editor_config.gfx_dir, "dive", "slash.png")).scaled(BLOCK_W, BLOCK_H, transformMode = Qt.Qt.SmoothTransformation)
    base_cross    = QImage(os.path.join(common.editor_config.gfx_dir, "dive", "cross.png")).scaled(BLOCK_W, BLOCK_H, transformMode = Qt.Qt.SmoothTransformation)
    base_special  = QImage(os.path.join(common.editor_config.gfx_dir, "dive", "special.png")).scaled(BLOCK_W, BLOCK_H, transformMode = Qt.Qt.SmoothTransformation)
    base_question = QImage(os.path.join(common.editor_config.gfx_dir, "dive", "question.png")).scaled(BLOCK_W, BLOCK_H, transformMode = Qt.Qt.SmoothTransformation)
    
    # Our specific blocks
    blk_booster  = replace_all_colors(base_booster, CLR_BOOSTER)
    blk_special  = replace_all_colors(base_special, CLR_SPECIAL)
    blk_normal   = replace_all_colors(base_normal, CLR_NORMAL)
    blk_a1       = replace_all_colors(base_normal, CLR_A1)
    blk_a2       = replace_all_colors(base_normal, CLR_A2)
    blk_a3       = replace_all_colors(base_normal, CLR_A3)
    blk_a1_cond  = replace_all_colors(base_question, CLR_A1)
    blk_a2_cond  = replace_all_colors(base_question, CLR_A2)
    blk_a3_cond  = replace_all_colors(base_question, CLR_A3)
    blk_pillar   = replace_all_colors(base_cross, CLR_PILLAR)
    blk_ramp     = replace_all_colors(base_special, CLR_RAMP)
    blk_end      = replace_all_colors(base_normal, CLR_END)
    blk_unknown  = replace_all_colors(base_question, CLR_UNKNOWN)
    blk_trigger  = replace_all_colors(base_question, CLR_NORMAL)
    blk_ob_spawn = replace_all_colors(base_slash, CLR_OBSTACLE)
    blk_ob_path  = replace_all_colors(base_special, CLR_OBSTACLE)
    
    out = QImage(img_w, img_h, QImage.Format_ARGB32_Premultiplied)
    out.fill(QColor(0, 0, 0, 255).rgba())
  
    painter = QPainter(out)
    
    x = 0
    y = 0
    for row in self.rows:
      x = 0
      for block_type in row:
        # --- Block Types ---
        # 00 -- Empty
        # 01 -- Green
        # 02 -- Booster
        # 03 -- Pillar
        # 04 -- Pillar
        # 05 -- Ramp
        # 06 -- Obstacle cube path
        # 07 -- Obstacle cube spawn point
        # 0A -- Triggers question 1
        # 0B -- Triggers question 2
        # 0C -- Triggers question 3
        # 14 -- Red (answer 1)
        # 1E -- Red (if Q1A1 is correct)
        # 1F -- Red (if Q2A1 is correct)
        # 20 -- Red (if Q3A1 is correct)
        # 28 -- Blue (answer 2)
        # 32 -- Blue (if Q1A2 is correct)
        # 33 -- Blue (if Q2A2 is correct)
        # 34 -- Blue (if Q3A2 is correct)
        # 3C -- Yellow (answer 3)
        # 46 -- Yellow (if Q1A3 is correct)
        # 47 -- Yellow (if Q2A3 is correct)
        # 48 -- Yellow (if Q3A3 is correct)
        # 64 -- Yellow
        # FF -- Rainbow, end of level
        if block_type == 0x00:
          block = None
        elif block_type == 0x01:
          block = blk_normal
        elif block_type == 0x02:
          block = blk_booster
        elif block_type in [0x03, 0x04]:
          block = blk_pillar
        elif block_type == 0x05:
          block = blk_ramp
        elif block_type == 0x06:
          block = blk_ob_path
        elif block_type == 0x07:
          block = blk_ob_spawn
        elif block_type in [0x0A, 0x0B, 0x0C]:
          block = blk_trigger
        elif block_type == 0x14:
          block = blk_a1
        elif block_type == 0x28:
          block = blk_a2
        elif block_type == 0x3C:
          block = blk_a3
        elif block_type in [0x1E, 0x1F, 0x20]:
          block = blk_a1_cond
        elif block_type in [0x32, 0x33, 0x34]:
          block = blk_a2_cond
        elif block_type in [0x46, 0x47, 0x48]:
          block = blk_a3_cond
        elif block_type == 0x64:
          block = blk_special
        elif block_type == 0xFF:
          block = blk_end
        else:
          block = blk_unknown
          print "  Unknown:", block_type
        
        if block:
          painter.drawImage(x, y, block)
        x += BLOCK_W
      
      y += BLOCK_H
    
    painter.end()
    
    return out

if __name__ == "__main__":
  ids = range(12) + range(21, 32) + range(41, 52)
  for id in ids:
    print "Dive", id
    dp = DiveParser()
    dp.load("logicaldive_level%02d.pak" % id)
    map = dp.render_map()
    map.save("wip/map%02d.png" % id)

### EOF ###