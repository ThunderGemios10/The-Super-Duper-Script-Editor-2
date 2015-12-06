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
from PyQt4.phonon import Phonon

import logging
import os

import common
from voice import get_voice_file, VoiceId

_LOGGER_NAME = common.LOGGER_NAME + "." + __name__
_LOGGER = logging.getLogger(_LOGGER_NAME)

class VoicePlayer:
  def __init__(self, parent = None):
    self.parent = parent
    
    self.next   = None
    self.player = Phonon.MediaObject()
    self.output = Phonon.AudioOutput(parent)
    self.path   = Phonon.createPath(self.player, self.output)
    
    self.player.stateChanged.connect(self.state_changed)
  
  ##############################################################################
  ### @fn   play()
  ##############################################################################
  def play(self, voice):
    
    voice_id = get_voice_file(voice)
    
    if voice_id == None:
      return
    
    voice_file = os.path.join(common.editor_config.voice_dir, "%04d.mp3" % voice_id)
    
    if not os.path.isfile(voice_file):
      QtGui.QMessageBox.warning(self.parent, "Could Not Find File", u"Could not locate\n%s" % voice_file)
      return
    
    if self.player.state() in [Phonon.LoadingState, Phonon.PausedState, Phonon.StoppedState]:
      self.player.setCurrentSource(Phonon.MediaSource(voice_file))
      self.player.play()
    
    else:
      # Don't try to compete with the changing of states, just request the player
      # stop and then tell it to play when we switch into a safer state.
      self.next = voice_file
      self.player.stop()
  
  ##############################################################################
  ### @fn   state_changed()
  ##############################################################################
  def state_changed(self, newstate, oldstate):
    if newstate in [Phonon.PausedState, Phonon.StoppedState]:
      if self.next:
        self.player.setCurrentSource(Phonon.MediaSource(self.next))
        self.player.play()
        self.next = None
    
    elif newstate == Phonon.ErrorState:
      _LOGGER.error(self.player.errorString())
  
  ##############################################################################
  ### @fn   stop()
  ##############################################################################
  def stop(self):
    self.player.stop()

### EOF ###