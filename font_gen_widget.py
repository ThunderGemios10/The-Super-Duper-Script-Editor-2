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

from PyQt4 import Qt, QtGui, QtCore
from PyQt4.QtCore import pyqtSignal
from ui.fontgenwidget import Ui_FontGenWidget

import common
from font_generator import FontConfig, gen_font, FONT_TYPES

# A few escapes for our substitutions.
SUB_ESCAPES = [
  ("\\n", "\n"),
  ("\\r", "\r"),
  ("\\t", "\t"),
]
def unescape(text):
  for escape in SUB_ESCAPES:
    text = text.replace(escape[0], escape[1])
  return text

def escape(text):
  for escape in SUB_ESCAPES:
    text = text.replace(escape[1], escape[0])
  return text

class FontGenWidget(QtGui.QWidget):
  ### SIGNALS ###
  modified = pyqtSignal()
  
  def __init__(self, parent = None):
    super(FontGenWidget, self).__init__(parent)
    
    self.ui = Ui_FontGenWidget()
    self.ui.setupUi(self)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    self.importing = True
    
    self.ui.treeSubs.clear()
    self.ui.treeSubs.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
    
    self.ui.cboPenCap.clear()
    self.ui.cboPenCap.addItem("Flat",   Qt.Qt.FlatCap)
    self.ui.cboPenCap.addItem("Square", Qt.Qt.SquareCap)
    self.ui.cboPenCap.addItem("Round",  Qt.Qt.RoundCap)
    
    self.ui.cboPenJoin.clear()
    self.ui.cboPenJoin.addItem("Miter",     Qt.Qt.MiterJoin)
    self.ui.cboPenJoin.addItem("Bevel",     Qt.Qt.BevelJoin)
    self.ui.cboPenJoin.addItem("Round",     Qt.Qt.RoundJoin)
    self.ui.cboPenJoin.addItem("SVG Miter", Qt.Qt.SvgMiterJoin)
    
    self.font_type = FONT_TYPES.font01
    
    self.importing = False
  
  ##############################################################################
  ### DATA FUNCTIONS
  ##############################################################################
  def get_data(self):
    return FontConfig(
      family    = self.font_name(),
      size      = self.font_size(),
      weight    = self.ui.spnFontWeight.value(),
      x_offset  = self.ui.spnXOffset.value(),
      y_offset  = self.ui.spnYOffset.value(),
      x_margin  = self.ui.spnXMargin.value(),
      y_margin  = self.ui.spnYMargin.value(),
      y_shift   = self.ui.spnYShift.value(),
      pen_size  = self.ui.spnPenSize.value(),
      pen_cap   = self.ui.cboPenCap.itemData(self.ui.cboPenCap.currentIndex()).toInt()[0],
      pen_join  = self.ui.cboPenJoin.itemData(self.ui.cboPenJoin.currentIndex()).toInt()[0],
      use_pen   = self.ui.chkTrace.isChecked(),
      chars     = common.qt_to_unicode(self.ui.txtChars.toPlainText()),
      subs      = self.get_subs(),
    )
  
  def import_data(self, config):
    # In case we're coming from pickled data that might
    # not have all the members we need.
    temp_config = config
    config = FontConfig()
    config.__dict__.update(temp_config.__dict__)
    
    # So we're not signaling a bunch of refreshes.
    self.importing = True
    
    self.ui.cboFont .setCurrentFont(QtGui.QFont(config.family))
    self.ui.spnFontSize   .setValue(config.size)
    self.ui.spnFontWeight .setValue(config.weight)
    self.ui.spnXOffset    .setValue(config.x_offset)
    self.ui.spnYOffset    .setValue(config.y_offset)
    self.ui.spnXMargin    .setValue(config.x_margin)
    self.ui.spnYMargin    .setValue(config.y_margin)
    self.ui.spnYShift     .setValue(config.y_shift)
    self.ui.spnPenSize    .setValue(config.pen_size)
    self.ui.chkTrace    .setChecked(config.use_pen)
    
    self.ui.cboPenCap .setCurrentIndex(self.ui.cboPenCap.findData(config.pen_cap))
    self.ui.cboPenJoin.setCurrentIndex(self.ui.cboPenJoin.findData(config.pen_join))
    
    self.ui.txtChars.setPlainText(config.chars)
    self.set_subs(config.subs)
    
    # All done~
    self.importing = False
    
    self.font_changed()
    self.update_preview()
  
  def font_name(self):
    return common.qt_to_unicode(self.ui.cboFont.currentFont().family(), normalize = False)
  
  def font_size(self):
    return self.ui.spnFontSize.value()
  
  ##############################################################################
  ### STUFF CHANGED
  ##############################################################################
  def chars_changed(self):
    if self.importing:
      return
    
    self.auto_update()
    self.modified.emit()
  
  def font_changed(self):
    if self.importing:
      return
  
    cursor = self.ui.txtChars.textCursor()
    
    self.ui.txtChars.selectAll()
    self.ui.txtChars.setFontFamily(self.ui.cboFont.currentFont().family())
    self.ui.txtChars.setFontPointSize(self.ui.spnFontSize.value())
    self.ui.txtChars.setFontWeight(self.ui.spnFontWeight.value())
    
    self.ui.txtChars.setTextCursor(cursor)
    
    self.auto_update()
    self.modified.emit()
  
  def adv_changed(self):
    if self.importing:
      return
    
    self.auto_update()
    self.modified.emit()
  
  def auto_update(self):
    if self.ui.chkAutoRefresh.isChecked():
      self.update_preview()
  
  def update_preview(self):
    if self.importing:
      return
    
    config = self.get_data()
    config.chars = config.chars[:256]
    
    font = gen_font([config], font_type = self.font_type, img_width = 256, draw_outlines = self.ui.chkBoundingBoxes.isChecked())
    # font.save("debug/test")
    
    qt_pixmap = QtGui.QPixmap.fromImage(font.trans.copy(0, 0, 256, 256))
    self.ui.lblPreview.setPixmap(qt_pixmap)
    
  ##############################################################################
  ### SUBSTITUTION FUNCTIONS
  ##############################################################################
  def add_sub(self, repl = u"?", repl_with = u"?"):
    new_sub = QtGui.QTreeWidgetItem([repl, repl_with])
    new_sub.setFlags(new_sub.flags() | Qt.Qt.ItemIsEditable)
    self.ui.treeSubs.addTopLevelItem(new_sub)
    
    if not self.importing:
      self.auto_update()
      self.modified.emit()
  
  def del_sub(self):
    rows = self.ui.treeSubs.selectionModel().selectedRows()
    
    for row in rows:
      self.ui.treeSubs.takeTopLevelItem(row.row())
    
    if not self.importing:
      self.auto_update()
      self.modified.emit()
  
  def sub_changed(self, item, col):
    # Make sure everything's valid.
    sub = common.qt_to_unicode(item.text(col))
    sub = unescape(sub)
    
    # The replacement column can only be single characters
    if col == 0:
      sub = sub[:1]
    
    sub = escape(sub)
    item.setText(col, sub)
    
    if not self.importing:
      self.auto_update()
      self.modified.emit()
  
  def set_subs(self, subs):
    
    self.ui.treeSubs.clear()
    for repl, repl_with in subs.items():
      repl      = escape(repl)
      repl_with = escape(repl_with)
      
      self.add_sub(repl, repl_with)
    
    if not self.importing:
      self.auto_update()
      self.modified.emit()
  
  def get_subs(self):
    # return {u"\t": u'  ', u"…":  u"..."}
    subs = {}
    
    for i in range(self.ui.treeSubs.topLevelItemCount()):
      item = self.ui.treeSubs.topLevelItem(i)
      
      repl      = unescape(common.qt_to_unicode(item.text(0)))
      repl_with = unescape(common.qt_to_unicode(item.text(1)))
      
      if len(repl) > 0:
        subs[repl] = repl_with
    
    return subs

if __name__ == '__main__':
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = FontGenWidget()
  form.show()
  sys.exit(app.exec_())

### EOF ###