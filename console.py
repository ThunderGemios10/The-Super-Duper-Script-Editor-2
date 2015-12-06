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

import logging

from PyQt4 import QtCore, QtGui, Qt

import common
from ui.console import Ui_Console

_LOGGER = logging.getLogger(common.LOGGER_NAME)
LEVELS  = ["Debug", "Info", "Warning", "Error", "Critical"]

class Console(QtGui.QDialog):
  def __init__(self, parent = None):
    super(Console, self).__init__(parent)
    
    self.ui = Ui_Console()
    self.ui.setupUi(self)
    
    self.ui.chkWordWrap.stateChanged.connect(lambda x: self.ui.txtConsole.setLineWrapMode(QtGui.QTextEdit.WidgetWidth if self.ui.chkWordWrap.isChecked() else QtGui.QTextEdit.NoWrap))
    
    self.creating = True
    
    cur_level = common.editor_config.log_level
    
    self.ui.cboLevels.clear()
    self.ui.cboLevels.addItems(LEVELS)
    
    index = self.ui.cboLevels.findText(cur_level, Qt.Qt.MatchExactly)
    self.ui.cboLevels.setCurrentIndex(index)
    
    _LOGGER.setLevel(cur_level.upper())
    self.ui.txtConsole.setLogger(_LOGGER)
    
    self.creating = False
  
  def updateLogLevel(self, level):
    if self.creating:
      return
    
    level = common.qt_to_unicode(level)
    _LOGGER.setLevel(level.upper())
    
    common.editor_config.log_level = level
    # common.editor_config.save_config()

def main():
  
  import sys

  app = QtGui.QApplication(sys.argv)
  app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
              app,
              QtCore.SLOT("quit()")
             )
  
  form = Console()
  logger = _LOGGER
  logger.debug("Test~")
  logger.info("Test~")
  logger.warning("Test~")
  logger.error("Test~")
  logger.critical("Test~")
  
  form.show()
  sys.exit(app.exec_())

if __name__ == "__main__":
  main()

### EOF ###