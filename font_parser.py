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

from PyQt4 import QtGui
from PyQt4.QtGui import QImage, QColor

from bitstring import ConstBitStream
import os.path
import re

from clt import CLT_STYLES

# BASE_DIR      = os.path.dirname(os.path.abspath(__file__))

# GFX_DIR         = common.editor_config.gfx_dir
# FONT_FOLDER   = os.path.join(GFX_DIR, "font")
FONT1_TABLE   = "Font01.font"
FONT2_TABLE   = "Font02.font"

SPFT_MAGIC     = ConstBitStream(hex='0x7446705304000000')

RE_DEFAULT_CLT = re.compile(ur"<CLT>", re.UNICODE | re.S)
RE_CLT         = re.compile(ur"\<CLT (?P<CLT_INDEX>\d+)\>", re.UNICODE | re.S)
RE_DIG         = re.compile(ur"<DIG.*?>", re.UNICODE | re.S)
RE_RUB         = re.compile(ur"<RUB.*?>.*?<RUB>", re.UNICODE | re.S)

FONT_DATA = { 1: {}, 2: {} }

def parse_font(font_num, spft_filename):
  
  FONT_DATA[font_num] = {}
  
  # spft_filename = ""
  
  # if font_num == 1:
    # spft_filename = os.path.join(FONT_FOLDER, FONT1_TABLE)
  # elif font_num == 2:
    # spft_filename = os.path.join(FONT_FOLDER, FONT2_TABLE)
  if not font_num in [1, 2]:
    print "Invalid font number. Valid values: 1, 2"
    return None
  
  # Header: 
  # 74467053 -- Magic
  # 04000000 -- Magic
  # XXXXXXXX -- Number of entries in font table
  # XXXXXXXX -- Position of first entry in font table
  # 
  # XXXXXXXX -- Number of chunks in the mappings table
  # XXXXXXXX -- Start position of mappings table (little-endian, as always)
  #             ***0x20000000 in both fonts I've seen
  # XXXXXXXX -- ????
  # XXXXXXXX -- ????
  # 
  # Character Mappings: from start pos (0x20) to (start pos + (# chunks * 2))
  #   * To avoid overcomplicating this, I'm just referring to the start pos as
  #     0x20 since I've only ever seen that value used.
  #   * Two-byte chunks (XXXX)
  #   * The position of each chunk, minus 0x20, divided by two (because they're
  #     two-byte chunks), equals the UTF-16 representation of a character.
  #     (i.e. pos 0x00A8: (0x00A8 - 0x20) / 2 = 0x0044 -> "A")
  #   * The value of each chunk is the index of that character in the font table,
  #     little-endian.
  #     (i.e. if the character "A" is the 35th entry, zero-indexed = 0x2200)
  #   * A chunk value of 0xFFFF means that character is not present in the font.
  spft = ConstBitStream(filename = spft_filename)
  
  magic = spft.read(64)
  
  if magic != SPFT_MAGIC:
    print "Didn't find SPFT magic."
    exit()
  
  num_entries = spft.read('uintle:32')
  table_start = spft.read('uintle:32')
  
  if num_entries == 0:
    print "No entries in SPFT table."
    return None
  
  if table_start * 8 > spft.len:
    print "Invalid SPFT table position."
    return None
  
  #print "Characters in font:", num_entries
  
  spft.pos = table_start * 8
  
  # Table:
  # * Entry:
  #   XXXX -- Character
  #   XXXX -- X Pos
  #   XXXX -- Y Pos
  #   XXXX -- Width
  #   XXXX -- Height
  #   0000 -- Padding
  #   0000 -- Padding
  #   FA08 -- Something to do with rendering offset. FA -> -6 -> renders six pixels down
  
  #print "    XXXX YYYY WWW HHH"
  
  for i in range(0, num_entries):
    char    = spft.read(16)
    char    = char.bytes.decode('utf-16le')    
    xpos    = spft.read('uintle:16')
    ypos    = spft.read('uintle:16')
    width   = spft.read('uintle:16')
    height  = spft.read('uintle:16')
    dummy   = spft.read('uintle:16')
    dummy   = spft.read('uintle:16')
    yshift  = spft.read('intle:8')
    dummy   = spft.read('uintle:8')
    
    info = {'x': xpos, 'y': ypos, 'w': width, 'h': height}
    FONT_DATA[font_num][char] = info
    
    #print "%3s %4d %4d %3d %3d" % (char.encode('cp932'), xpos, ypos, width, height)

def parse_string(string, default_clt = 0):
  
  string = RE_DEFAULT_CLT.sub("<CLT %d>" % default_clt, string)
  string = RE_DIG.sub("00", string)
  string = RE_RUB.sub("", string)
  
  clt_changes = {}
  
  while True:
    match = RE_CLT.search(string)
    
    if match == None:
      break
    
    clt_val = match.groupdict(default = default_clt)["CLT_INDEX"]
    
    if clt_val == None:
      clt_val = default_clt
    else:
      clt_val = int(clt_val)
    
    clt_changes[match.start()] = clt_val
    
    string = string[:match.start()] + string[match.end():]
    #print string
  
  return string, clt_changes
  
def get_len(string, default_clt = 0):
  
  string, clt_changes = parse_string(string, default_clt)
  
  cur_font = CLT_STYLES[default_clt].font
  cur_scale = CLT_STYLES[default_clt].scale / 100.0
  cur_xshift = CLT_STYLES[default_clt].x_shift
  
  total_width = 0
  
  lengths = []
  
  for i in range(len(string)):
    if i in clt_changes:
      clt = clt_changes[i]
      if not clt in CLT_STYLES:
        clt = default_clt
        clt_changes[i] = default_clt
      cur_font = CLT_STYLES[clt].font
      cur_scale = CLT_STYLES[clt].scale / 100.0
      cur_xshift = CLT_STYLES[clt].x_shift
    
    if string[i] in FONT_DATA[cur_font]:
      char_width = FONT_DATA[cur_font][string[i]]['w'] * cur_scale
      #print string[i], char_width
    else:
      # This is the character the game uses to replace unknown characters.
      char_width = FONT_DATA[cur_font][u'\u2261']['w'] * cur_scale
    char_width += cur_xshift
    
    total_width = total_width + char_width
    
    lengths.append(char_width)
  
  return string, lengths, clt_changes

def font_bmp_to_alpha(filename):
  
  image = QImage(filename)
  image = image.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  # Because the game uses 8bit grayscale bitmaps for its fonts with white as
  # fully visible and black as fully transparent, I'm using a naive technique
  # that averages the RGB value of a pixel and sets that as its alpha value.
  # I'm sure this will do fun stuff to other images, but it does the job
  # for the game's fonts, and that's all that really matters. ヽ(´ー｀)ノ
  for i in range(image.width()):
    for j in range(image.height()):
      color = QColor(image.pixel(i, j))
      alpha = (color.red() + color.green() + color.blue()) / 3
      color.setAlpha(alpha)
      image.setPixel(i, j, color.rgba())
  
  return image

# parse_font(1)
# parse_font(2)

if __name__ == '__main__':
  
  parse_font(2, r"Y:\Danganronpa\Danganronpa2\!workspace\fonts\font.pak\0003.font")
  # parse_font(2, "X:/Danganronpa/Editor/data/gfx/font/font02.font")

  # print "             W   H".encode('utf-8')
  # for char in sorted(FONT_DATA[1].keys()):
    # info = FONT_DATA[1][char]
    # if info['w'] % 12 > 0:
    # print ("U+%04X %3s %3d %3d" % (ord(char), char, info['w'], info['h'])).encode('utf-8')
  print ''.join(sorted(FONT_DATA[2].keys())).encode('utf-8')

### EOF ###