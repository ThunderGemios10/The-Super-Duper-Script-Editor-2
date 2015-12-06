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
from PyQt4.QtGui import QImage, QPainter, QColor, QLabel, QMatrix, QPixmap
from PyQt4.QtCore import QRect, QRectF

from ui.nonstopplayer import Ui_NonstopPlayer

import copy
import math
import os.path
import re
import sys
import time

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)

import common
import font_parser
from nonstop import NonstopParser
from sprite import SPRITE_TYPE
from text_format import TextFormat, TEXT_FORMATS, TEXT_ORIENT
from text_printer import print_text, process_text, get_trial, get_sprite
# import text_printer
from voice_player import VoicePlayer

class NonstopPlayer(QtGui.QDialog):
  def __init__(self, parent = None):
    super(NonstopPlayer, self).__init__(parent)
    
    self.ui = Ui_NonstopPlayer()
    self.ui.setupUi(self)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.lblSprite = QLabel(self.ui.lblPreview)
    self.lblSprite.setGeometry(0, 0, 480, 272)
    
    self.nonstop = None
    
    self.line   = 0
    self.lines  = []
    self.labels = []
    
    self.ui.actionSaveImg = QtGui.QAction("Save image...", None, triggered = self.saveImage)
    self.ui.actionSaveImg.setShortcut("Ctrl+S")
    self.addAction(self.ui.actionSaveImg)
    
    self.voice_player = VoicePlayer()
    self.auto_play    = True
  
  def load(self, filename):
    self.nonstop = NonstopParser()
    self.nonstop.load(filename)
    
    if len(self.nonstop.script_pack) == 0:
      return
    
    self.bg = get_trial(self.nonstop.script_pack[0].scene_info, show_box = False, show_sprite = False)
    qt_pixmap = QtGui.QPixmap.fromImage(self.bg)
    self.ui.lblPreview.setPixmap(qt_pixmap)
    
    self.lines = []
    for i in range(len(self.nonstop.lines)):
      if self.nonstop.script_pack[i][common.editor_config.lang_trans] != "":
        text = self.nonstop.script_pack[i][common.editor_config.lang_trans]
      else:
        text = self.nonstop.script_pack[i][common.editor_config.lang_orig]
      
      format = self.nonstop.script_pack[i].scene_info.format
      text_img = get_text(text, common.SCENE_MODES.debate, format)
      
      self.lines.append(QtGui.QPixmap.fromImage(text_img))
    
    self.anims  = [None] * len(self.nonstop.lines)
    self.labels = [None] * len(self.nonstop.lines)
    self.timers = [None] * len(self.nonstop.lines)
  
  def start(self):
    self.line = 0
    self.show_line(self.line)
  
  def _finished(self, line):
    self.labels[line].deleteLater()
  
  def show_line(self, line, queue_next = True):
    
    scene_info = self.nonstop.script_pack[line].scene_info
    voice  = scene_info.voice
    format = scene_info.format
    sprite_id = scene_info.sprite
    sprite_id.sprite_type = SPRITE_TYPE.stand
    sprite = get_sprite(sprite_id)
    
    if self.auto_play:
      self.voice_player.play(voice)
    
    if sprite:
      qt_pixmap = QtGui.QPixmap.fromImage(sprite)
      self.lblSprite.setPixmap(qt_pixmap)
    
    text_img  = self.lines[line]
    line_info = self.nonstop.lines[line]
    
    matrix = QMatrix()
    matrix.rotate(line_info.rot_angle - (90 if format.orient == TEXT_ORIENT.ver else 0))
    text_img = text_img.transformed(matrix, Qt.Qt.SmoothTransformation)
    
    time_visible = line_info.time_visible / 60.0
    
    width_start  = text_img.width() * line_info.zoom_start / 100.0
    height_start = text_img.height() * line_info.zoom_start / 100.0
    width_end    = width_start * ((line_info.zoom_change / 100.0) ** time_visible)
    height_end   = height_start * ((line_info.zoom_change / 100.0) ** time_visible)
    
    x_start = line_info.x_start - (width_start / 2.0)
    y_start = line_info.y_start - (height_start / 2.0)
    x_vel   = line_info.velocity * math.cos(math.radians(90 - line_info.angle))
    y_vel   = -line_info.velocity * math.sin(math.radians(90 - line_info.angle))
    
    x_end = x_start + (x_vel * time_visible) - ((width_end - width_start) / 2.0)
    y_end = y_start + (y_vel * time_visible) - ((height_end - height_start) / 2.0)
    
    self.labels[line] = QLabel(self.ui.lblPreview)
    self.labels[line].setScaledContents(True)
    self.labels[line].setGeometry(x_start, y_start, text_img.width(), text_img.height())
    self.labels[line].setPixmap(text_img)
    self.labels[line].show()
    
    self.anims[line] = QtCore.QPropertyAnimation(self.labels[line], "geometry")
    self.anims[line].setDuration(time_visible * 1000)
    self.anims[line].setStartValue(QRectF(x_start, y_start, width_start, height_start))
    self.anims[line].setEndValue(QRectF(x_end, y_end, width_end, height_end))
    self.anims[line].finished.connect(lambda: self._finished(line))
    
    self.anims[line].start(QtCore.QAbstractAnimation.DeleteWhenStopped)
    
    if queue_next:
      next_line = line + 1
      if next_line < len(self.lines):
        self.timers[line] = QtCore.QTimer()
        self.timers[line].timeout.connect(lambda: self.show_line(next_line, queue_next = True))
        self.timers[line].setSingleShot(True)
        self.timers[line].start(line_info.delay / 60.0 * 1000)
    
  ##############################################################################
  ### @fn   saveImage()
  ### @desc Saves a preview image. :D
  ##############################################################################
  def saveImage(self):
  
    dir   = "ss"
    index = 0
    
    if not os.path.isdir(dir):
      if os.path.isfile(dir):
        return
      else:
        os.mkdir(dir)
    
    while True:
      if index >= 9999:
        return
        
      filename = os.path.join(dir, ("shot%04d.png" % index))
      
      if not os.path.isfile(filename):
        break
        
      index = index + 1
    
    if not os.path.isdir(dir):
      os.mkdir(dir)
    
    self.lblText.pixmap().save(filename)

##############################################################################
### @fn   get_text(text)
### @desc Gets an image with the given text.
##############################################################################
def get_text(text, scene_mode = common.SCENE_MODES.debate, format = TextFormat(), mangle = True):

  lines, lengths, clt_changes = process_text(text, scene_mode, format, False)
  
  # For our borders, since I'm lazy.
  margin = 1
  img_h  = len(lines) * format.h + (margin * 2)
  img_w  = 0
  x, y   = 0, 0
  
  for length in lengths:
    width = sum(length) + (margin * 2)
    if width > img_w:
      img_w = width
  
  if format.orient == TEXT_ORIENT.ver:
    img_w, img_h = img_h, img_w + format.h
    x = img_w - format.h - margin
  
  out = QImage(img_w, img_h, QImage.Format_ARGB32_Premultiplied)
  out.fill(QColor(0, 0, 0, 0).rgba())
  
  new_format = copy.copy(format)
  new_format.x = x
  new_format.y = y
  new_format.w = img_w
  
  return print_text(out, text, scene_mode, new_format, mangle)

if __name__ == "__main__":
  # test = get_text(u"<CLT 17>アイロンが停電の\n引き金<CLT>ならば…", common.SCENE_MODES.debate, TEXT_FORMATS[common.SCENE_MODES.debate], False)
  # test.save("ss/test.png")
  
  # app = QtGui.QApplication(sys.argv)
  
  # test = VoicePlayer()
  # test.play(VoiceId(0, 99, 0))

  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  filename = None
  if len(sys.argv) > 1:
    filename = sys.argv[1].decode(sys.stdin.encoding)
  
  if not filename:
    exit()
  
  form = NonstopPlayer()
  form.load(filename)
  # form.load("hanron_01_001.dat") # f
  # form.load("hanron_01_002.dat") # m
  # form.load("hanron_01_003.dat") # m
  # form.load("hanron_02_001.dat") # m
  # form.load("hanron_02_002.dat") # f
  # form.load("hanron_03_001.dat") # m
  # form.load("hanron_03_002.dat") # f
  # form.load("hanron_04_001.dat") # f
  # form.load("hanron_04_002.dat") # m
  # form.load("hanron_04_003.dat") # m
  # form.load("hanron_05_001.dat") # m
  # form.load("hanron_05_002.dat") # f
  form.start()
  form.show()
  
  sys.exit(app.exec_())

### EOF ###