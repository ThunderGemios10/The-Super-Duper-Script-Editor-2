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
from PyQt4.QtGui import QImage, QPainter, QColor, QPixmap, QBitmap, QTransform
from PyQt4.QtCore import QRect, QRectF

from enum import Enum
import ctypes
import os.path
import re
import sys
import time

import common

from clt import CLT_STYLES
import font_parser
from font_parser import FONT_DATA
from object_labels import get_char_name, get_ammo_name, get_present_name
from text_files import load_text
from text_format import TextFormat, TEXT_ALIGN, TEXT_ORIENT, TEXT_FORMATS
from sprite import get_sprite_file, SPRITE_TYPE

################################################################################
### VARIABLES
################################################################################
IMG_W           = 480
IMG_H           = 272

# BASE_DIR        = os.path.dirname(os.path.abspath(__file__))

# GFX_DIR         = os.path.join(BASE_DIR, "data/gfx")
GFX_DIR         = common.editor_config.gfx_dir
AMMO_DIR        = os.path.join(GFX_DIR, "ammo")
ANAGRAM_DIR     = os.path.join(GFX_DIR, "anagram")
BG_DIR          = os.path.join(GFX_DIR, "bg")
BGD_DIR         = os.path.join(GFX_DIR, "bgd")
CUTIN_DIR       = os.path.join(GFX_DIR, "cutin")
FLASH_DIR       = os.path.join(GFX_DIR, "flash")
FONT_DIR        = os.path.join(GFX_DIR, "font")
GALLERY_DIR     = os.path.join(GFX_DIR, "gallery")
MENU_DIR        = os.path.join(GFX_DIR, "menu")
MOVIE_DIR       = os.path.join(GFX_DIR, "movies")
PRESENT_DIR     = os.path.join(GFX_DIR, "presents")
SPRITE_DIR      = os.path.join(GFX_DIR, "sprites")
TEXTBOX_DIR     = os.path.join(GFX_DIR, "textbox")
TRIAL_DIR       = os.path.join(GFX_DIR, "trial")

IMG_FILTERS  = Enum("unfiltered", "sepia", "inverted")

FONTS = {}

################################################################################
### FUNCTIONS
################################################################################

##############################################################################
### @fn   load_fonts()
### @desc Loads the two font images.
##############################################################################
def load_fonts():
  FONTS[1] = QImage(os.path.join(FONT_DIR, "Font01.png"))
  FONTS[2] = QImage(os.path.join(FONT_DIR, "Font02.png"))
  
  font_parser.parse_font(1, os.path.join(FONT_DIR, "Font01.font"))
  font_parser.parse_font(2, os.path.join(FONT_DIR, "Font02.font"))

##############################################################################
### @fn   replace_all_colors(image, color)
### @desc Replaces all colors in the image with the given color.
##############################################################################
def replace_all_colors(image, color):
  
  new_img = image.copy()
  
  if not new_img.format() is QImage.Format_ARGB32_Premultiplied:
    new_img = new_img.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  color_img = QImage(new_img.width(), new_img.height(), QImage.Format_ARGB32_Premultiplied)
  color_img.fill(color.rgba())
  
  painter = QPainter(new_img)
  painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
  painter.drawImage(new_img.rect(), color_img, color_img.rect())
  painter.end()
  
  return new_img

##############################################################################
### @fn   add_v_gradient(image, colors)
### @desc Paints a vertical gradient over the image from colors[0] to colors[i]
##############################################################################
def add_v_gradient(image, colors):
  
  if len(colors) < 2:
    return image
  
  new_img = image.copy()
  
  if not new_img.format() is QImage.Format_ARGB32_Premultiplied:
    new_img = new_img.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  gradient = QtGui.QLinearGradient(0, 0, 0, new_img.height())
  
  gradient.setColorAt(0, colors[0])
  
  for i in range(1, len(colors) - 1):
    gradient.setColorAt(i / len(colors), colors[i])
  
  gradient.setColorAt(1, colors[-1])
  
  painter = QPainter(new_img)
  painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
  painter.fillRect(new_img.rect(), gradient)
  painter.end()
  
  return new_img

##############################################################################
### @fn   add_border(image, color, size)
### @desc Adds a colored border to the image "size" pixels large.
##############################################################################
def add_border(image, color, size):

  w = image.width()
  h = image.height()
  
  out = QImage(w + (size * 2), h + (size * 2), QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())
  
  #border = image.scaled(w, h, Qt.Qt.KeepAspectRatioByExpanding, Qt.Qt.FastTransformation)
  border = replace_all_colors(image, color)
  
  painter = QPainter(out)
  
  for i in range(0, (size * 2) + 1):
    for j in range(0, (size * 2) + 1):
      painter.drawImage(QRectF(i, j, w, h), border, QRectF((border.rect())))
  
  painter.drawImage(QRect(size, size, w, h), image, image.rect())
  painter.end()
  
  return out

##############################################################################
### @fn   filter_image(image)
### @desc Filters the image.
###       The DLL crashes on app quit for whatever reason,
###       so this presently does nothing at all. <_>
##############################################################################
def filter_image(image, filter):
  if filter == IMG_FILTERS.unfiltered:
    return image
  
  out = image.copy()
  # So we know we have 32 bits
  out.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  if filter == IMG_FILTERS.sepia:
    pass
    # Slow as all hell.
    #def to_sepia(color):
    #  gray = QtGui.qGray(color)
    #  sepia_r = gray * 255 / 255
    #  sepia_g = gray * 240 / 255
    #  sepia_b = gray * 192 / 255
    #  sepia_a = QtGui.qAlpha(color)
    #  #return QtGui.qRgba(sepia_r, sepia_g, sepia_b, sepia_a)
    #  return sepia_r, sepia_g, sepia_b, sepia_a
    #
    #bpp = out.byteCount() / (out.width() * out.height())
    #assert bpp == 4 # Why would it be anything else?
    #
    #for j in range(out.height()):
    #  scanline = out.scanLine(j)
    #  scanline.setsize(out.bytesPerLine())
    #  QRgba* line = (QRgba*)out.scanLine(j)
    #  
    #  for i in range(out.width()):
    #    pixel = scanline[i * bpp : (i + 1) * bpp]
    #    b, g, r, a = ord(pixel[0]), ord(pixel[1]), ord(pixel[2]), ord(pixel[3])
    #    sepia_r, sepia_g, sepia_b, sepia_a = to_sepia(QtGui.qRgba(r, g, b, a))
    #    pixel[0] = chr(sepia_b)
    #    pixel[1] = chr(sepia_g)
    #    pixel[2] = chr(sepia_r)
    #    pixel[3] = chr(sepia_a)
  
  elif filter == IMG_FILTERS.inverted:
    out.invertPixels()
  
  #pixels_ptr = ctypes.c_void_p(out.bits().__int__())
  #img = filters.image(pixels_ptr, out.width(), out.height(), out.width(), out.height())
  
  #g_val = 32
  #filters.flatten(img, filters.rgb(g_val, g_val, g_val), filters.sepia)
  #filters.brightness(img, 32)
  #filters.contrast(img, 164)
  #filters.desaturate(img, 0.15)
  
  return out

##############################################################################
### @fn   draw_centering_guides(image, target_x, target_y, target_w, guide_h)
### @desc Draws two vertical red lines surrounding the given area
###       to be used to assist in centering text.
##############################################################################
def draw_centering_guides(image, target_x, target_y, target_w, guide_h):
  
  left_x = target_x - (target_w / 2.0)
  right_x = left_x + target_w
  
  top_y = target_y
  bottom_y = top_y + guide_h
  
  new_img = image.copy()
  
  if not new_img.format() is QImage.Format_ARGB32_Premultiplied:
    new_img = new_img.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  painter = QPainter(new_img)
  
  pen = painter.pen()
  pen.setColor(QColor(255, 0, 0))
  painter.setPen(pen)
  
  painter.drawLine(left_x, top_y, left_x, bottom_y)
  painter.drawLine(right_x, top_y, right_x, bottom_y)
  
  painter.end()
  
  return new_img

def get_nametag(char_id, x, y, color, vertical = False):
  
  w = IMG_W
  h = IMG_H
  
  nametag = get_char_name(char_id, common.editor_config.data01_dir)
  if nametag == None:
    nametag = "NAMETAG MISSING"
  
  if vertical:
    nametag_img = QImage(h, w, QImage.Format_ARGB32_Premultiplied)
    
    new_x   = h - y
    new_y   = x
    x       = new_x
    y       = new_y
  else:
    nametag_img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
  
  format = TextFormat(x = x, y = y, w = 25, h = 25, align = TEXT_ALIGN.left, orient = TEXT_ORIENT.hor, clt = 0)
  nametag_img = print_text(nametag_img, nametag, None, format = format, mangle = False)
  
  if vertical:
    matrix = QTransform()
    matrix.rotate(-90)
    nametag_img = nametag_img.transformed(matrix)
  
  nametag_img = replace_all_colors(nametag_img, color)
  
  return nametag_img

##############################################################################
### @fn   get_sprite(sprite_id)
### @desc Returns the sprite for the specified sprite ID.
##############################################################################
def get_sprite(sprite_id):

  sprite_file = get_sprite_file(sprite_id)
  
  if sprite_file == None:
    return None
  
  sprite_file = os.path.join(SPRITE_DIR, sprite_file)
  
  if not os.path.isfile(sprite_file):
    sprite_file = os.path.join(SPRITE_DIR, "bustup_%02d_%02d.png" % (99, 99))
  
  out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())
  painter = QPainter(out)
  
  sprite = QImage(sprite_file)
  
  # Center the sprite on our image.
  sprite_x = (out.width() - sprite.width()) / 2
  sprite_y = 0
  
  painter.drawImage(QRect(sprite_x, sprite_y, sprite.width(), sprite.height()), sprite, sprite.rect())
  painter.end()
  
  return out

##############################################################################
### @fn   get_bg(room_id)
### @desc Returns the background image for the specified room ID.
##############################################################################
def get_bg(room_id):
  
  if room_id == -1:
    return None
  
  bg_file = os.path.join(BG_DIR, "bg_%03d.png" % room_id)
  
  if not os.path.isfile(bg_file):
    bg_file = os.path.join(BG_DIR, "bg_%03d.png" % 999)
  
  out = QImage(bg_file)
  if not out.format == QImage.Format_ARGB32_Premultiplied:
    out = out.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  return out

##############################################################################
### @fn   get_bgd(bgd_id)
### @desc Returns the background image for the specified CG background.
##############################################################################
def get_bgd(bgd_id):
  
  if bgd_id == -1:
    return None
  
  bgd_file = os.path.join(BGD_DIR, "bgd_%03d.png" % bgd_id)
  
  if not os.path.isfile(bgd_file):
    bgd_file = os.path.join(BG_DIR, "%04d.png" % 9999)
  
  out = QImage(bgd_file)
  if not out.format == QImage.Format_ARGB32_Premultiplied:
    out = out.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  return out

##############################################################################
### @fn   get_ammo(ammo_id, x, y)
### @desc Returns the specified ammo.
##############################################################################
def get_ammo(ammo_id, x, y):
  
  if ammo_id == -1:
    return None
  
  ammo_file =        os.path.join(AMMO_DIR, "kotodama_ico_%03d.png" % ammo_id)
  ammo_border_file = os.path.join(AMMO_DIR, "border.png")
  
  if not os.path.isfile(ammo_file):
    ammo_file = os.path.join(AMMO_DIR, "kotodama_ico_%03d.png" % 999)
  
  ammo  = QImage(ammo_file)
  border = QImage(ammo_border_file)
  
  x_pos = x
  y_pos = y
  
  border_x = x_pos - ((border.width() - ammo.width()) / 2)
  border_y = y_pos - ((border.height() - ammo.height()) / 2)
  
  out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())
  painter = QPainter(out)
  
  painter.drawImage(QRect(x_pos, y_pos, ammo.width(), ammo.height()), ammo, ammo.rect())
  painter.drawImage(QRect(border_x, border_y, border.width(), border.height()), border, border.rect())
  
  painter.end()
  
  return out

##############################################################################
### @fn   get_ammo_ingame(ammo_id)
### @desc Returns the specified ammo.
##############################################################################
def get_ammo_ingame(ammo_id):
  
  x_pos = 144
  y_pos = 59
  
  return get_ammo(ammo_id, x_pos, y_pos)

##############################################################################
### @fn   get_ammo_menu(ammo_id)
### @desc Returns the specified ammunition icon.
##############################################################################
def get_ammo_menu(ammo_id):
  
  x_pos = 35
  y_pos = 80
  
  return get_ammo(ammo_id, x_pos, y_pos)

##############################################################################
### @fn   get_cutin(cutin_id)
### @desc Returns the specified cutin.
##############################################################################
def get_cutin(cutin_id):
  
  if cutin_id == -1:
    return None
  
  cutin_file =        os.path.join(CUTIN_DIR, "cutin_ico_%03d.png" % cutin_id)
  cutin_border_file = os.path.join(CUTIN_DIR, "border.png")
  
  if not os.path.isfile(cutin_file):
    cutin_file = os.path.join(CUTIN_DIR, "cutin_ico_%03d.png" % 999)
  
  cutin  = QImage(cutin_file)
  border = QImage(cutin_border_file)
  
  x_pos = 307
  y_pos = 91
  
  border_x = x_pos - ((border.width() - cutin.width()) / 2)
  border_y = y_pos - ((border.height() - cutin.height()) / 2)
  
  out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())
  painter = QPainter(out)
  
  painter.drawImage(QRect(x_pos, y_pos, cutin.width(), cutin.height()), cutin, cutin.rect())
  painter.drawImage(QRect(border_x, border_y, border.width(), border.height()), border, border.rect())
  
  painter.end()
  
  return out

##############################################################################
### @fn   get_flash(flash_id)
### @desc Returns the background image for the specified flash event.
##############################################################################
def get_flash(flash_id):
  
  if flash_id == -1:
    return None
  
  flash_file = os.path.join(FLASH_DIR, "fla_%03d.png" % flash_id)
  
  if not os.path.isfile(flash_file):
    flash_file = os.path.join(FLASH_DIR, "fla_%03d.png" % 999)
  
  out = QImage(flash_file)
  if not out.format == QImage.Format_ARGB32_Premultiplied:
    out = out.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  return out

##############################################################################
### @fn   get_movie(movie_id)
### @desc Returns the background image for the specified movie.
##############################################################################
def get_movie(movie_id):
  
  if movie_id == -1:
    return None
  
  movie_file = os.path.join(MOVIE_DIR, "movie_%02d.png" % movie_id)
  
  if not os.path.isfile(movie_file):
    movie_file = os.path.join(MOVIE_DIR, "movie_%02d.png" % 99)
  
  out = QImage(movie_file)
  if not out.format == QImage.Format_ARGB32_Premultiplied:
    out = out.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  return out

##############################################################################
### @fn   get_present(file_id)
### @desc Returns the specified present icon.
##############################################################################
def get_present(file_id, x_pos, y_pos):
  
  icon_file = os.path.join(PRESENT_DIR, "present_ico_%03d.png" % file_id)
  
  if not os.path.isfile(icon_file):
    icon_file = os.path.join(PRESENT_DIR, "present_ico_non.png")
  
  icon = QImage(icon_file)
  
  out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())  
  painter = QPainter(out)
  
  painter.drawImage(QRect(x_pos, y_pos, icon.width(), icon.height()), icon, icon.rect())
  
  painter.end()
  
  return out

def get_present_menu(present_id):
  
  x_pos = 35
  y_pos = 80
  
  return get_present(present_id, x_pos, y_pos)

def get_present_ingame(present_id):
  
  x_pos = 144
  y_pos = 59
  
  return get_present(present_id, x_pos, y_pos)

##############################################################################
### @fn   get_event_icon(file_id)
### @desc Returns the specified event icon.
##############################################################################
def get_event_icon(file_id):
  
  icon_file = os.path.join(GALLERY_DIR, "gallery_thumbnail_e_%03d.png" % file_id)
  
  if not os.path.isfile(icon_file):
    icon_file = os.path.join(GALLERY_DIR, "gallery_ico_e_none.png")
  
  icon = QImage(icon_file)
  
  x_pos = 278
  y_pos = 66
  
  out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())  
  painter = QPainter(out)
  
  painter.drawImage(QRect(x_pos, y_pos, icon.width(), icon.height()), icon, icon.rect())
  
  painter.end()
  
  return out

##############################################################################
### @fn   get_movie_icon(file_id)
### @desc Returns the specified movie icon.
##############################################################################
def get_movie_icon(file_id):
  
  icon_file   = os.path.join(GALLERY_DIR, "gallery_thumbnail_m_%03d.png" % file_id)
  
  if not os.path.isfile(icon_file):
    icon_file = os.path.join(GALLERY_DIR, "gallery_ico_m_none.png")
  
  icon   = QImage(icon_file)
  
  x_pos = 310
  y_pos = 66
  
  out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())  
  
  painter = QPainter(out)
  painter.drawImage(QRect(x_pos, y_pos, icon.width(), icon.height()), icon, icon.rect())
  painter.end()
  
  return out

##############################################################################
### @fn   get_artwork_icon(file_id)
### @desc Returns the specified movie icon.
##############################################################################
def get_artwork_icon(file_id):
  
  icon_file   = os.path.join(GALLERY_DIR, "gallery_thumbnail_a_%03d.png" % file_id)
  
  if not os.path.isfile(icon_file):
    icon_file = os.path.join(GALLERY_DIR, "gallery_ico_a_none.png")
  
  icon   = QImage(icon_file)
  
  x_pos = 326
  y_pos = 66
  
  out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())  
  
  painter = QPainter(out)
  painter.drawImage(QRect(x_pos, y_pos, icon.width(), icon.height()), icon, icon.rect())
  painter.end()
  
  return out

##############################################################################
### @fn   get_box(scene_info)
### @desc Returns the text box specified by the given scene info.
##############################################################################
def get_box(scene_info):
  
  mode       = scene_info.mode
  box_color  = scene_info.box_color
  box_type   = scene_info.box_type
  speaking   = scene_info.speaking
  speaker_id = scene_info.speaker
  headshot   = scene_info.headshot
  chapter    = scene_info.chapter
  
  if box_color != common.BOX_COLORS.yellow and box_color != common.BOX_COLORS.green and box_color != common.BOX_COLORS.blue:
    box_color = common.BOX_COLORS.yellow
  
  out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())
  
  painter = QPainter(out)
  painter.setRenderHint(QPainter.Antialiasing, True)
  
  # Some commonality between the boxes.
  box     = QImage()
  button  = QImage()
  
  nametag_x     = 0
  nametag_y     = 0
  nametag_color = QColor(255, 255, 255, 255)
  nametag_vert  = False
  
  if box_type == common.BOX_TYPES.flat:
    box    = QImage(os.path.join(TEXTBOX_DIR, "box_gray.png"))
    button = QImage(os.path.join(TEXTBOX_DIR, "button_%s.png" % box_color))
    
    nametag_x     = 10
    nametag_y     = 176
    nametag_color = QColor(255, 255, 255, 255)
    nametag_vert  = False
  
  elif box_type == common.BOX_TYPES.novel:
    box = QImage(os.path.join(TEXTBOX_DIR, "box_novel.png"))
  
  elif box_type == common.BOX_TYPES.normal:
    
    if mode == common.SCENE_MODES.normal:
      
      box    = QImage(os.path.join(TEXTBOX_DIR, "box.png"))
      button = QImage(os.path.join(TEXTBOX_DIR, "button_%s.png" % box_color))
      
      nametag_x     = 0
      nametag_y     = 220
      nametag_color = QColor(50, 50, 50, 255)
      nametag_vert  = True
  
      if not box.format() is QImage.Format_ARGB32_Premultiplied:
        box = box.convertToFormat(QImage.Format_ARGB32_Premultiplied)
      
      box_painter = QPainter(box)
      box_painter.setRenderHint(QPainter.Antialiasing, True)
      
      if speaker_id == 0: # Main character gets a special text box.
        namebox = QImage(os.path.join(TEXTBOX_DIR, "name_%s_mc.png" % box_color))
      else:
        namebox = QImage(os.path.join(TEXTBOX_DIR, "name_%s.png" % box_color))
        
      box_painter.drawImage(box.rect(), namebox, namebox.rect())
      
      box_painter.end()
    
    elif mode == common.SCENE_MODES.trial:
      
      box_base = QImage(os.path.join(TRIAL_DIR, "trial_box.png"))
      banner   = QImage(os.path.join(TRIAL_DIR, "trial_banner.png"))
      
      if speaker_id == 0: # Main character gets a special text box.
        namebox = QImage(os.path.join(TRIAL_DIR, "trial_name_mc.png"))
      else:
        namebox = QImage(os.path.join(TRIAL_DIR, "trial_name.png"))
      
      if not headshot == None:
        case_num = QImage(os.path.join(TRIAL_DIR, "case_%02d.png" % chapter))
        headshot = QImage(os.path.join(TRIAL_DIR, "headshot", "%02d.png" % headshot))
        underlay = QImage(os.path.join(TRIAL_DIR, "trial_headshot.png"))
      else:
        case_num = QImage()
        underlay = QImage()
        headshot = QImage()
      
      button = QImage(os.path.join(TRIAL_DIR, "button.png"))
      nametag_x     = 12
      nametag_y     = 168
      nametag_color = QColor(255, 255, 255, 255)
      nametag_vert  = False
      
      box = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
      box.fill(QColor(0, 0, 0, 0).rgba())
      
      box_painter = QPainter(box)
      box_painter.setRenderHint(QPainter.Antialiasing, True)
      
      box_painter.drawImage(box.rect(), banner,   banner.rect())
      box_painter.drawImage(box.rect(), namebox,  namebox.rect())
      box_painter.drawImage(box.rect(), box_base, box_base.rect())
      box_painter.drawImage(box.rect(), underlay, underlay.rect())
      box_painter.drawImage(box.rect(), headshot, headshot.rect())
      box_painter.drawImage(box.rect(), case_num, case_num.rect())
      
      box_painter.end()
    
    else:
      box = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
      box.fill(QColor(0, 0, 0, 0).rgba())
  
  painter.drawImage(out.rect(), box,     box.rect())
  painter.drawImage(out.rect(), button,  button.rect())
  
  if not speaker_id == None:
    nametag = get_nametag(speaker_id, nametag_x, nametag_y, nametag_color, nametag_vert)
    painter.drawImage(out.rect(), nametag, nametag.rect())
  
  painter.end()
  
  return out

##############################################################################
### @fn   get_normal(scene_info, show_bg = True, show_sprite = True, show_box = True)
### @desc Returns an image containing the scene in normal mode.
##############################################################################
def get_normal(scene_info, show_bg = True, show_sprite = True, show_box = True):
  
  sprite_id = scene_info.sprite
  room_id = scene_info.room
  scene_id = scene_info.scene
  
  out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())
  
  painter = QPainter(out)
  painter.setRenderHint(QPainter.Antialiasing, True)
  
  if show_bg:
    if scene_info.movie >= 0:
      bg = get_movie(scene_info.movie)
    elif scene_info.flash >= 0:
      bg = get_flash(scene_info.flash)
    elif scene_info.bgd >= 0:
      bg = get_bgd(scene_info.bgd)
    else:
      bg = get_bg(room_id)
    
    if bg:
      painter.drawImage(out.rect(), bg, bg.rect())
  
  if show_sprite:
    sprite = get_sprite(sprite_id)
    if sprite:
      painter.drawImage(out.rect(), sprite, sprite.rect())
  
  if not scene_info.img_filter == IMG_FILTERS.unfiltered:
    painter.end()
    out = filter_image(out, scene_info.img_filter)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.Antialiasing, True)
  
  if show_box:
    box = get_box(scene_info)
    painter.drawImage(out.rect(), box, box.rect())
  
  painter.end()
  
  return out

##############################################################################
### @fn   get_trial(scene_info, show_bg = True, show_sprite = True, show_box = True)
### @desc Returns an image containing the scene in trial mode.
##############################################################################
def get_trial(scene_info, show_bg = True, show_sprite = True, show_box = True):
  
  case_num = scene_info.chapter
  sprite_id = scene_info.sprite
  
  if case_num > 6 or case_num <= 0:
    case_num = 1
  
  out = None
  
  if show_bg:
    if scene_info.movie >= 0:
      out = get_movie(scene_info.movie)
    elif scene_info.flash >= 0:
      out = get_flash(scene_info.flash)
    elif scene_info.bgd >= 0:
      out = get_bgd(scene_info.bgd)
    else:
      # out = QImage(os.path.join(BG_DIR, "bg_%03d.png" % (199 + case_num)))
      out = get_bg(199 + case_num)
  else:
    out = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
    out.fill(QColor(0, 0, 0, 0).rgba())
  
  if not out.format() is QImage.Format_ARGB32_Premultiplied:
    out = out.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  painter = QPainter(out)
  painter.setRenderHint(QPainter.Antialiasing, True)
  
  if show_sprite:
    sprite_id.sprite_type = SPRITE_TYPE.stand
    
    sprite = get_sprite(sprite_id)
    if sprite:
      painter.drawImage(out.rect(), sprite, sprite.rect())
  
  if not scene_info.img_filter == IMG_FILTERS.unfiltered:
    painter.end()
    out = filter_image(out, scene_info.img_filter)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.Antialiasing, True)
  
  if show_box:
  
    box = get_box(scene_info)
    painter.drawImage(out.rect(), box, box.rect())
  
  return out

##############################################################################
### @fn   get_letter(clt, char)
### @desc Returns an image containing the letter rendered with the given CLT.
##############################################################################
def get_letter(clt, char):
  
  if not clt in CLT_STYLES:
    clt = 0
  
  font    = CLT_STYLES[clt].font
  hscale  = CLT_STYLES[clt].scale / 100.0
  vscale  = CLT_STYLES[clt].scale / 100.0
  
  try:
    info = FONT_DATA[font][char]
  except:
    # This is the character the game replaces unknown characters with.
    info = FONT_DATA[font][u'\u2261']
  
  expand_l = 0
  expand_r = 0
  expand_t = 0
  expand_b = 0
  
  box = QRect(info['x'] - expand_l, info['y'] - expand_t, info['w'] + expand_l + expand_r, info['h'] + expand_t + expand_b)
  #box = QRect(info['x'] - expand_l, info['y'] - expand_t, info['w'], info['h'])
  
  expand_l += CLT_STYLES[clt].border_size
  expand_r += CLT_STYLES[clt].border_size
  expand_t += CLT_STYLES[clt].border_size
  expand_b += CLT_STYLES[clt].border_size
  
  xshift = -expand_l
  yshift = +expand_t
  
  if font == 1:
    yshift += 0
  elif font == 2:
    yshift -= 2
  
  final_w = info['w']
  final_h = info['h']
  
  if hscale != 1.0:
    final_w = (final_w * hscale)
  
  if vscale != 1.0:
    old_h   = final_h
    final_h = (final_h * vscale)
    
    yshift = yshift + ((old_h - final_h) / 2.0)
  
  final_w += expand_l + expand_r
  final_h += expand_t + expand_b
  
  letter = FONTS[CLT_STYLES[clt].font].copy(box)
  
  if hscale != 1.0 or vscale != 1.0:
    matrix = QTransform()
    matrix.scale(hscale, vscale)
    letter = letter.transformed(matrix, Qt.Qt.SmoothTransformation)
  
  top_color = CLT_STYLES[clt].top_color
  bottom_color = CLT_STYLES[clt].bottom_color
  
  if top_color and not bottom_color:
    letter = replace_all_colors(letter, top_color)
  elif top_color and bottom_color:
    letter = add_v_gradient(letter, [top_color, bottom_color])

  border_size  = CLT_STYLES[clt].border_size
  border_color = CLT_STYLES[clt].border_color
  
  if border_size:
    letter = add_border(letter, border_color, border_size)
  
  return letter, (xshift, yshift, final_w, final_h)

##############################################################################
### @fn   mangle_line(line, lengths, scene_mode, cur_font)
### @desc Hack the line up a bit to reflect how it'll show up in-game
###       based on some in-game quirks.
##############################################################################
def mangle_line(line, scene_mode):
  
  # If it doesn't have a category, assume it's safe.
  if scene_mode == common.SCENE_MODES.other:
    return line

  # The game auto-wraps after 54 characters.
  # Not that we should ever run into an issue with that.
  # max_len = 54
  max_len = 96
  
  # Replace extra characters with something ugly
  # so it's easy to know it needs to be fixed.
  too_long  = u'\u2261'
  
  # The max length is even tighter 
  if scene_mode == common.SCENE_MODES.ammo or scene_mode == common.SCENE_MODES.present:
    max_len = 61
  
  elif scene_mode == common.SCENE_SPECIAL.option:
    max_len = 54
  
  elif scene_mode == common.SCENE_MODES.help:
    max_len = 87
  
  extra_chars = len(line) - max_len
  if extra_chars > 0:
    line = line[:max_len] + (too_long * extra_chars)
  
  return line

##############################################################################
### @fn   process_text(text, scene_mode, format, mangle)
### @desc Converts the given text into three lists: lines, lengths, and CLT changes.
##############################################################################
def process_text(text, scene_mode, format, mangle = True):
  
  # Replace our unmarked CLTs with whatever default CLT we're given.
  # Also start the line off with the default CLT so we're definitely using it.
  # Useful for modes like Nonstop Debate, where text is normally CLT 16.
  text = "<CLT>" + text
  text = re.sub("<CLT>", "<CLT %d>" % format.clt, text)
  
  lines = []
  lengths = []
  clt_changes = []
  last_clt = format.clt
  
  for line in text.split("\n"):
    # Start the line off with the last-used CLT, so the parsers know what it is.
    line = ("<CLT %d>" % last_clt) + line
    line, length, clt = font_parser.get_len(line, format.clt)
    
    # Hack the line up a bit to reflect how it'll show up in-game
    # based on some in-game quirks.
    if mangle:
      line = mangle_line(line, scene_mode)
    
    # If there isn't an initial CLT, start the line off with
    # the CLT still in use at the end of the previous line.
    if not 0 in clt.keys():
      clt[0] = last_clt
    
    last_clt = clt[max(clt.keys())]
    
    # If we're supposed to skip blanks and this line is blank
    # after parsing the formatting, then don't add it to the list.
    if format.kill_blanks and line.strip() == "":
      continue
    
    lines.append(line)
    lengths.append(length)
    clt_changes.append(clt)
  
  return lines, lengths, clt_changes

##############################################################################
### @fn   print_text(image, text, scene_mode = common.SCENE_MODES.normal)
### @desc Prints the given text onto the given image.
##############################################################################
def print_text(image, text, scene_mode = common.SCENE_MODES.normal, format = TextFormat(), mangle = True):
  
  img_w = IMG_W
  img_h = IMG_H
  
  if image:
    img_w = image.width()
    img_h = image.height()
    
  out = QImage(img_w, img_h, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())
  
  painter = QPainter(out)
  # This is a better representation of how the game handles text.
  painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
  painter.setRenderHint(QPainter.Antialiasing, True)
  
  lines, lengths, clt_changes = process_text(text, scene_mode, format, mangle)
  
  base_x      = format.x
  base_y      = format.y
  line_height = format.h
  
  x, y = base_x, base_y
  cur_clt = 0
  
  text_height = len(lines) * line_height
  while text_height + y > img_h:
    y -= line_height
      
  center_x = format.x + (format.w / 2.0)
  right_x  = format.x + format.w
  
  for i, line in enumerate(lines):
    # Only bother if we actually see the line.
    if y > -line_height and y < img_h:
      line_length = sum(lengths[i])
      
      if format.orient == TEXT_ORIENT.hor:
        if format.align == TEXT_ALIGN.left:
          x = base_x
        elif format.align == TEXT_ALIGN.right:
          x = right_x - line_length
        elif format.align == TEXT_ALIGN.center:
          x = center_x - (line_length / 2.0)
        elif format.align == TEXT_ALIGN.offcenter:
          x = center_x - (line_length / 2.0) - 7
      
      for j in range(len(line)):
        char = line[j]
        
        if j in clt_changes[i]:
          cur_clt = clt_changes[i][j]
        
        letter, (xshift, yshift, final_w, final_h) = get_letter(cur_clt, char)
        
        final_x = (x + xshift)
        final_y = (y + yshift) + max(0, (line_height - final_h)) + CLT_STYLES[cur_clt].y_shift
        
        painter.drawImage(QRect(final_x, final_y, final_w, final_h), letter, letter.rect())
        
        if format.orient == TEXT_ORIENT.hor:
          x += lengths[i][j]
        elif format.orient == TEXT_ORIENT.ver:
          y += lengths[i][j]
    
    if format.orient == TEXT_ORIENT.hor:
      y += line_height
    elif format.orient == TEXT_ORIENT.ver:
      y  = base_y
      x -= line_height
    
  # And, last but not least, draw the image underneath everything.
  if image:
    painter.drawImage(out.rect(), image, image.rect())
  
  painter.end()
  return out

##############################################################################
### @fn   draw_anagram(anagram)
### @desc Draws an Epiphany Anagram scene based on the given info.
##############################################################################
def draw_anagram(anagram):
  
  BOX_LEFT      = 4
  BOX_TOP       = 22
  BOX_X_OFFSET  = 31
  BOX_Y_OFFSET  = 61
  
  TEXT_X_OFFSET = 13
  TEXT_Y_OFFSET = 9
  TEXT_CLT      = 8
  FONT          = CLT_STYLES[TEXT_CLT].font
  
  MAX_LETTERS   = 15
  
  BOX = QImage(os.path.join(ANAGRAM_DIR, "box.png"))
  QUESTION = QImage(os.path.join(ANAGRAM_DIR, "question.png"))
  out = QImage(os.path.join(ANAGRAM_DIR, "bg.png"))
  
  text = anagram.solution[common.editor_config.lang_trans]
  
  if len(text) == 0:
    return out
  
  if not out.format() is QImage.Format_ARGB32_Premultiplied:
    out = out.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  painter = QPainter(out)
  painter.setRenderHint(QPainter.Antialiasing, True)
  
  # Put them in a list so it's easier to loop.
  visible = [range(1, len(text) + 1), anagram.easy, anagram.normal, anagram.hard]
  
  x = BOX_LEFT
  y = BOX_TOP
  
  for row in range(len(visible)):
    
    if not visible[row] == None:
      for i, char in enumerate(text):
      
        if (i + 1) in visible[row]:
          
          painter.drawImage(QRect(x, y, BOX.width(), BOX.height()), BOX, BOX.rect())
          
          # Get info on our current letter.
          letter, (xshift, yshift, final_w, final_h) = get_letter(TEXT_CLT, char)
          painter.drawImage(QRect(x + TEXT_X_OFFSET + xshift, y + TEXT_Y_OFFSET + yshift, final_w, final_h), letter, letter.rect())
        
        else:
          painter.drawImage(QRect(x, y, QUESTION.width(), QUESTION.height()), QUESTION, QUESTION.rect())
        
        x += BOX_X_OFFSET
      
    x = BOX_LEFT
    y += BOX_Y_OFFSET
  
  painter.end()
  
  return out

##############################################################################
### @fn   draw_scene(scene_info, text = None)
### @desc Wrapper function for most of the above stuff.
###       Calls the necessary functions to construct the scene based on
###       the given scene information.
##############################################################################
def draw_scene(scene_info, text = None):
  bg = None
  max_length = 0
  kill_blanks = False
  
  if scene_info.mode in [common.SCENE_MODES.normal, common.SCENE_MODES.normal_flat]:
    bg = get_normal(scene_info)
    
    if scene_info.box_type == common.BOX_TYPES.flat:
      scene_info.mode = common.SCENE_MODES.normal_flat
    else:
      scene_info.mode = common.SCENE_MODES.normal
    
  elif scene_info.mode == common.SCENE_MODES.trial:
    bg = get_trial(scene_info)
  
  elif scene_info.mode == common.SCENE_MODES.novel:
    scene_info.box_type = common.BOX_TYPES.novel
    bg = get_normal(scene_info)
  
  elif scene_info.mode == common.SCENE_MODES.rules:
    bg = QImage(os.path.join(MENU_DIR, "rules.png"))
  
  elif scene_info.mode == common.SCENE_MODES.ammo:
    bg = QImage(os.path.join(MENU_DIR, "ammo-desc.png"))
    overlay = get_ammo(scene_info.file_id, 254, 117)
  
    if not bg.format() is QImage.Format_ARGB32_Premultiplied:
      bg = bg.convertToFormat(QImage.Format_ARGB32_Premultiplied)
    
    painter = QPainter(bg)
    painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
    painter.drawImage(bg.rect(), overlay, overlay.rect())
    painter.end()
    
    name = get_ammo_name(scene_info.file_id)
    if name:
      bg = print_text(bg, name, common.SCENE_MODES.ammoname, TEXT_FORMATS[common.SCENE_MODES.ammoname], False)
  
  elif scene_info.mode == common.SCENE_MODES.ammoname:
    bg = QImage(os.path.join(MENU_DIR, "ammo-list.png"))
    overlay = get_ammo(scene_info.file_id, 254, 61)
  
    if not bg.format() is QImage.Format_ARGB32_Premultiplied:
      bg = bg.convertToFormat(QImage.Format_ARGB32_Premultiplied)
    
    painter = QPainter(bg)
    painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
    painter.drawImage(bg.rect(), overlay, overlay.rect())
    painter.end()
  
  elif scene_info.mode == common.SCENE_MODES.present:
    bg = QImage(os.path.join(MENU_DIR, "present-desc.png"))
    overlay = get_present(scene_info.file_id, 248, 96)
  
    if not bg.format() is QImage.Format_ARGB32_Premultiplied:
      bg = bg.convertToFormat(QImage.Format_ARGB32_Premultiplied)
    
    painter = QPainter(bg)
    painter.drawImage(bg.rect(), overlay, overlay.rect())
    painter.end()
    
    name = get_present_name(scene_info.file_id)
    if name:
      bg = print_text(bg, name, common.SCENE_MODES.presentname, TEXT_FORMATS[common.SCENE_MODES.presentname], False)
  
  elif scene_info.mode == common.SCENE_MODES.presentname:
    bg = QImage(os.path.join(MENU_DIR, "present-list.png"))
    overlay = get_present(scene_info.file_id, 248, 46)
  
    if not bg.format() is QImage.Format_ARGB32_Premultiplied:
      bg = bg.convertToFormat(QImage.Format_ARGB32_Premultiplied)
    
    painter = QPainter(bg)
    painter.drawImage(bg.rect(), overlay, overlay.rect())
    painter.end()
  
  elif scene_info.mode == common.SCENE_MODES.menu:
    bg = QImage(os.path.join(MENU_DIR, "menu.png"))
  
  elif scene_info.mode == common.SCENE_MODES.report or scene_info.mode == common.SCENE_MODES.report2:
    bg = QImage(os.path.join(MENU_DIR, "report.png"))
  
  elif scene_info.mode == common.SCENE_MODES.skill or scene_info.mode == common.SCENE_MODES.skill2:
    bg = QImage(os.path.join(MENU_DIR, "skills.png"))
  
  elif scene_info.mode == common.SCENE_MODES.map:
    bg = QImage(os.path.join(MENU_DIR, "map.png"))
  
  elif scene_info.mode == common.SCENE_MODES.music:
    bg = QImage(os.path.join(MENU_DIR, "soundtest.png"))
  
  elif scene_info.mode in [common.SCENE_MODES.eventname, common.SCENE_MODES.moviename, common.SCENE_MODES.artworkname]:
    bg = QImage(os.path.join(MENU_DIR, "gallery.png"))
    
    if scene_info.mode == common.SCENE_MODES.eventname:
      overlay = get_event_icon(scene_info.file_id)
    elif scene_info.mode == common.SCENE_MODES.moviename:
      overlay = get_movie_icon(scene_info.file_id)
    elif scene_info.mode == common.SCENE_MODES.artworkname:
      overlay = get_artwork_icon(scene_info.file_id)
  
    if not bg.format() is QImage.Format_ARGB32_Premultiplied:
      bg = bg.convertToFormat(QImage.Format_ARGB32_Premultiplied)
    
    painter = QPainter(bg)
    painter.drawImage(bg.rect(), overlay, overlay.rect())
    painter.end()
  
  elif scene_info.mode == common.SCENE_MODES.theatre:
    bg = get_normal(scene_info)
  
  elif scene_info.mode == common.SCENE_MODES.debate or scene_info.mode == common.SCENE_MODES.hanron:
    bg = get_trial(scene_info, show_box = False)
    
  else:
    bg = QImage(IMG_W, IMG_H, QImage.Format_ARGB32_Premultiplied)
    bg.fill(QColor(0, 0, 0, 255).rgba())
  
  if not bg.format() is QImage.Format_ARGB32_Premultiplied:
    bg = bg.convertToFormat(QImage.Format_ARGB32_Premultiplied)
  
  if scene_info.cutin != -1:
    cutin = get_cutin(scene_info.cutin)
    
    painter = QPainter(bg)
    painter.drawImage(bg.rect(), cutin, cutin.rect())
    painter.end()
  
  if scene_info.ammo != -1:
    ammo = get_ammo_ingame(scene_info.ammo)
    
    painter = QPainter(bg)
    painter.drawImage(bg.rect(), ammo, ammo.rect())
    painter.end()
  
  if scene_info.present != -1:
    present = get_present_ingame(scene_info.present)
    
    painter = QPainter(bg)
    painter.drawImage(bg.rect(), present, present.rect())
    painter.end()
  
  if scene_info.special == common.SCENE_SPECIAL.option:
    overlay = QImage(os.path.join(TEXTBOX_DIR, "option_bar.png"))
    painter = QPainter(bg)
    painter.drawImage(bg.rect(), overlay, overlay.rect())
    painter.end()
    
    if not text == None and not text == "":
      bg = print_text(bg, text, common.SCENE_SPECIAL.option, TEXT_FORMATS[common.SCENE_SPECIAL.option], False)
      
  if not text == None and not text == "":
    bg = print_text(bg, text, scene_info.mode, TEXT_FORMATS[scene_info.mode])
  
  return bg

# Anyone using this needs the fonts, so let's go at it.
load_fonts()

if __name__ == "__main__":
  # def get_text(text, scene_mode = common.SCENE_MODES.normal)
  #test = get_text("<CLT 3>Who the hell do you\nthink you are?!", common.SCENE_MODES.normal, False)
  test = QImage(os.path.join(SPRITE_DIR, "bustup_05_13.png"))
  test = filter_image(test, IMG_FILTERS.sepia)
  test.save("ss/test.png")

### EOF ###