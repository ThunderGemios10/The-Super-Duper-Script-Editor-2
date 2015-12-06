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

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtGui import QFont, QFontMetrics, QImage, QPainter, QPainterPath, QColor

import logging
import math
import os
import sys

from bitstring import BitStream
from enum import Enum

import common
from font_parser import SPFT_MAGIC

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

FONT_TYPES = Enum("font01", "font02")
GAMES = Enum("dr", "sdr2")

LINE_HEIGHT   = {FONT_TYPES.font01: 20, FONT_TYPES.font02: 26}
MAX_HEIGHT    = 2048
HEIGHT_FACTOR = 128

# UNKNOWN1 is different for every font I've seen.
UNKNOWN1 = {
  GAMES.dr: {
    FONT_TYPES.font01: BitStream(hex = '0x2D000000'),
    FONT_TYPES.font02: BitStream(hex = '0x30000000'),
  },
  GAMES.sdr2: {
    FONT_TYPES.font01: BitStream(hex = '0x24000000'),
    FONT_TYPES.font02: BitStream(hex = '0x30000000'),
  }
}

UNKNOWN2 = BitStream(hex = '0x01000000')

class FontData:
  def __init__(self):
    self.data = []
  
  def save(self, filename, font_type = FONT_TYPES.font01, game = GAMES.dr):
    data = BitStream(SPFT_MAGIC)
    
    data += BitStream(uintle = len(self.data), length = 32)
    
    mapping_table_len = self.find_max_char() + 1 # zero-indexed so +1 for the size.
    mapping_table_start = 0x20
    font_table_start = mapping_table_len * 2 + mapping_table_start
    
    data += BitStream(uintle = font_table_start, length = 32)
    data += BitStream(uintle = mapping_table_len, length = 32)
    data += BitStream(uintle = mapping_table_start, length = 32)
    data += UNKNOWN1[game][font_type] + UNKNOWN2
    
    data += self.gen_mapping_table(mapping_table_len)
    
    data += self.gen_font_table()
    
    padding = BitStream(hex = '0x00') * (16 - ((data.len / 8) % 16))
    
    data += padding
    
    f = open(filename, "wb")
    data.tofile(f)
    f.close()
  
  # Returns the character with the highest hex value in UTF16
  def find_max_char(self):
    
    max_char = BitStream(hex = '0x0000')
    
    for entry in self.data:
      char = BitStream(bytes = bytearray(entry['char'], encoding = 'utf-16le'))
      
      if char.uintle > max_char.uintle:
        max_char = char
    
    return max_char.uintle
  
  def gen_mapping_table(self, num_entries):
    mapping_table = BitStream(hex = '0xFFFF') * num_entries
    
    for i, entry in enumerate(self.data):
      char = BitStream(bytes = bytearray(entry['char'], encoding = 'utf-16le'))
      
      entry_pos = char.uintle * 2 * 8 # Bytes -> Bits
      
      mapping_table[entry_pos : entry_pos + 16] = BitStream(uintle = i, length = 16)
    
    return mapping_table
  
  def gen_font_table(self):
    font_table = BitStream()
    
    padding = BitStream(hex = "0x00000000")
    
    for entry in self.data:
      char    = BitStream(bytes = bytearray(entry['char'], encoding = 'utf-16le'))
      x_pos   = BitStream(uintle = entry['x'], length = 16)
      y_pos   = BitStream(uintle = entry['y'], length = 16)
      width   = BitStream(uintle = entry['w'], length = 16)
      height  = BitStream(uintle = entry['h'], length = 16)
      y_shift = BitStream(intle  = entry['y_shift'], length = 8)
      unknown = BitStream(hex = "0x08")
      
      font_table += char + x_pos + y_pos + width + height + padding + y_shift + unknown
    
    return font_table

class GameFont:
  def __init__(self, width = 512):
    self.trans  = QImage(width, MAX_HEIGHT, QImage.Format_ARGB32_Premultiplied)
    self.trans.fill(QColor(0, 0, 0, 0).rgba())
    
    self.opaque = QImage(width, MAX_HEIGHT, QImage.Format_ARGB32_Premultiplied)
    self.opaque.fill(QColor(0, 0, 0, 255).rgba())
    
    self.font_data = FontData()
  
  def save(self, directory, name, for_game = True, for_editor = True, font_type = FONT_TYPES.font01, game = GAMES.dr):
    # name = str(font_type)
    
    if for_editor:
      self.trans.save(os.path.join(directory, name + ".png"))
    
    if for_game:
      opaque_gray = to_gray(self.opaque)
      opaque_gray.save(os.path.join(directory, name + ".bmp"))
    
    self.font_data.save(os.path.join(directory, name + ".font"), font_type, game)

class FontConfig:
  def __init__(self, family = "Meiryo", size = 11, weight = 50,
      x_offset = 0, y_offset = 2, x_margin = 2, y_margin = 2,
      y_shift = -1, pen_size = 0, pen_cap = Qt.Qt.RoundCap,
      pen_join = Qt.Qt.RoundJoin, use_pen = False, chars = "",
      subs = {u"\t": u'  '}):
    
    self.family   = family
    self.size     = size
    self.weight   = weight
    self.x_offset = x_offset
    self.y_offset = y_offset
    self.x_margin = x_margin
    self.y_margin = y_margin
    self.y_shift  = y_shift
    self.pen_size = pen_size
    self.pen_cap  = pen_cap
    self.pen_join = pen_join
    self.use_pen  = use_pen
    
    self.chars    = chars
    self.subs     = subs
  
def to_gray(image):
  out = QImage(image.width(), image.height(), QImage.Format_Indexed8)
  color_table = []
  
  for i in range(256):
    color_table.append(QtGui.qRgb(i, i, i))
  
  out.setColorTable(color_table)
  
  for i in range(image.width()):
    for j in range(image.height()):
      color = image.pixel(i, j)
      out.setPixel(i, j, QtGui.qGray(color))
  
  return out

def gen_font(font_configs, font_type = FONT_TYPES.font01, img_width = 1024, draw_outlines = False):
  img_height = HEIGHT_FACTOR
  
  seen_chars = []
  
  game_font = GameFont(width = img_width)
  painter = QPainter(game_font.trans)
  
  text_brush = QtGui.QBrush(QColor(255, 255, 255, 255))
  painter.setBrush(text_brush)
  
  outline_brush = QtGui.QBrush()
  outline_pen   = QtGui.QPen(QColor(255, 0, 0, 255), 1, style = Qt.Qt.DotLine, join = Qt.Qt.MiterJoin)
  
  x_pos = 0
  y_pos = 0
  
  line_height = LINE_HEIGHT[font_type]
  
  for config in font_configs:
    font = QFont(config.family, config.size, config.weight, italic = False)
    font.setKerning(False)
    metric = QFontMetrics(font)
    
    painter.setFont(font)
    painter.setRenderHint(QPainter.TextAntialiasing, True)
    painter.setRenderHint(QPainter.Antialiasing, True)
    
    text_pen = painter.pen()
    text_pen.setBrush(QColor(255, 255, 255, 255))
    text_pen.setWidthF(config.pen_size)
    text_pen.setCapStyle(config.pen_cap)
    text_pen.setJoinStyle(config.pen_join)
    text_pen.setStyle(Qt.Qt.SolidLine if config.use_pen else Qt.Qt.NoPen)
    painter.setPen(text_pen)
    
    for char in sorted(config.chars):
      
      if char in seen_chars:
        continue
      else:
        seen_chars.append(char)
      
      # If we want a character to represent something it's not.
      char_to_print = char
      
      if char in config.subs:
        char_to_print = config.subs[char]
      
      char_w = metric.width(char_to_print)
      
      if x_pos + char_w > img_width:
        x_pos = 0
        y_pos += line_height + config.y_margin
      
      if y_pos < 0:
        y_pos = 0
    
      if y_pos + line_height > MAX_HEIGHT:
        _LOGGER.warning("Ran out of vertical space. Generated font does not include all characters.")
        break
    
      game_font.font_data.data.append({'char': char, 'x': x_pos, 'y': y_pos, 'w': char_w, 'h': line_height, 'y_shift': config.y_shift})
      
      path = QPainterPath()
      path.addText(x_pos + config.x_offset, y_pos + metric.ascent() + config.y_offset, font, char_to_print)
      painter.drawPath(path)
      
      if draw_outlines:
        painter.setBrush(outline_brush)
        painter.setPen(outline_pen)
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        painter.drawRect(x_pos, y_pos, char_w, line_height)
        
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(text_brush)
        painter.setPen(text_pen)
      
      x_pos += char_w + config.x_margin
  
  painter.end()
  
  painter = QPainter(game_font.opaque)
  painter.drawImage(game_font.opaque.rect(), game_font.trans, game_font.trans.rect())
  painter.end()
  
  # Crop our images so they only take up as much space as they need.
  final_height = int(math.ceil(float(y_pos + line_height) / float(HEIGHT_FACTOR)) * HEIGHT_FACTOR)
  game_font.trans   = game_font.trans.copy(0, 0, img_width, final_height)
  game_font.opaque  = game_font.opaque.copy(0, 0, img_width, final_height)
  
  return game_font

# if __name__ == '__main__':
  
  # app = QtGui.QApplication(sys.argv)
  
  # chars = load_text(CHAR_LIST)
  # We can't have dupes, and why not put them in order while we're at it?
  # chars = sorted(make_unique(chars))
  
  # game_font = gen_font(chars)
  # game_font.save(SAVE_AS)

### EOF ###