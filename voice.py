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

import os

################################################################################
### CONSTANTS
################################################################################
CH_1      = 1
CH_2      = 2
CH_3      = 3
CH_4      = 4
CH_5      = 5
CH_6      = 6
CH_GEN    = 99
# I don't know what the hell this game is doing.
CH_GEN_2  = 100
CH_GEN_3  = 101
CH_GEN_4  = 102
CH_GEN_5  = 103

VOICE_OFFSETS = {
  # Hinata
  0x00: {CH_1:  565, CH_2:  745, CH_3:  926, CH_4: 1134, CH_5: 1354, CH_6: 1610, CH_GEN: 1848, CH_GEN_2: 1889, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Komaeda
  0x01: {CH_1: 2175, CH_2: 2358, CH_3: 2467, CH_4: 2626, CH_5:   -1, CH_6: 2804, CH_GEN: 2805, CH_GEN_2: 2905, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Togami
  0x02: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6: 8532, CH_GEN: 8533, CH_GEN_2: 8605, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Tanaka
  0x03: {CH_1: 8108, CH_2: 8144, CH_3: 8174, CH_4: 8243, CH_5:   -1, CH_6: 8394, CH_GEN: 8395, CH_GEN_2: 8470, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Souda
  0x04: {CH_1: 7553, CH_2: 7579, CH_3: 7618, CH_4: 7671, CH_5: 7785, CH_6: 7909, CH_GEN: 8001, CH_GEN_2: 8077, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Hanamura
  0x05: {CH_1:  364, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6:  470, CH_GEN:  471, CH_GEN_2:  547, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Nidai
  0x06: {CH_1: 5631, CH_2: 5682, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6: 5736, CH_GEN: 5737, CH_GEN_2: 5818, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Kuzuryuu
  0x07: {CH_1: 2994, CH_2: 3024, CH_3: 3122, CH_4: 3194, CH_5: 3269, CH_6: 3387, CH_GEN: 3495, CH_GEN_2: 3576, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Owari
  0x08: {CH_1: 5871, CH_2: 5896, CH_3: 5926, CH_4: 6007, CH_5: 6099, CH_6: 6201, CH_GEN: 6292, CH_GEN_2: 6374, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Nanami
  0x09: {CH_1: 4920, CH_2: 4966, CH_3: 5046, CH_4: 5144, CH_5: 5227, CH_6: 5463, CH_GEN: 5514, CH_GEN_2: 5594, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Sonia
  0x0A: {CH_1: 6971, CH_2: 6993, CH_3: 7021, CH_4: 7075, CH_5: 7184, CH_6: 7328, CH_GEN: 7428, CH_GEN_2: 7518, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Saionji
  0x0B: {CH_1: 6727, CH_2: 6771, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6: 6892, CH_GEN: 6893, CH_GEN_2: 6956, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Koizumi
  0x0C: {CH_1: 2034, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6: 2099, CH_GEN: 2100, CH_GEN_2: 2164, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Tsumiki
  0x0D: {CH_1: 8614, CH_2: 8654, CH_3: 8702, CH_4:   -1, CH_5:   -1, CH_6: 8843, CH_GEN: 8844, CH_GEN_2: 8918, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Mioda
  0x0E: {CH_1: 3638, CH_2: 3678, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6: 3732, CH_GEN: 3733, CH_GEN_2: 3806, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Pekoyama
  0x0F: {CH_1: 6430, CH_2: 6471, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6: 6616, CH_GEN: 6617, CH_GEN_2: 6699, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Monokuma
  0x10: {CH_1: 3837, CH_2: 3865, CH_3: 3884, CH_4: 3899, CH_5: 3920, CH_6: 3958, CH_GEN: 4029, CH_GEN_2: 4129, CH_GEN_3: 4160, CH_GEN_4: 4277, CH_GEN_5: 4424},
  # Monomi
  0x11: {CH_1: 4435, CH_2: 4458, CH_3: 4478, CH_4: 4492, CH_5: 4511, CH_6: 4544, CH_GEN: 4545, CH_GEN_2: 4645, CH_GEN_3:   -1, CH_GEN_4: 4651, CH_GEN_5: 4722},
  # Enoshima
  0x12: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6:    0, CH_GEN:  343, CH_GEN_2:   -1, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Mecha Nidai
  0x13: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6:   -1, CH_GEN:   -1, CH_GEN_2:   -1, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Naegi
  0x14: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6: 4727, CH_GEN: 4902, CH_GEN_2: 4903, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Kirigiri
  0x15: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6: 1980, CH_GEN:   -1, CH_GEN_2: 2021, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Togami (Real)
  0x16: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6: 8482, CH_GEN:   -1, CH_GEN_2: 8519, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Hanamura's Mom
  0x17: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6:   -1, CH_GEN:   -1, CH_GEN_2:  359, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Alter Ego
  0x18: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6:   -1, CH_GEN:   -1, CH_GEN_2:   -1, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Mini Nidai
  0x19: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6:   -1, CH_GEN:   -1, CH_GEN_2:   -1, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Monokuma & Monomi
  0x1A: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6:   -1, CH_GEN:   -1, CH_GEN_2:   -1, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
  # Monomi no Mahoutsukai Narrator
  0x1B: {CH_1:   -1, CH_2:   -1, CH_3:   -1, CH_4:   -1, CH_5:   -1, CH_6:   -1, CH_GEN:   -1, CH_GEN_2: 3623, CH_GEN_3:   -1, CH_GEN_4:   -1, CH_GEN_5:   -1},
}

################################################################################
### 
################################################################################

class VoiceId():
  def __init__(
    self,
    char_id = -1,
    chapter = -1,
    voice_id = -1
  ):
    self.char_id  = char_id
    self.chapter  = chapter
    self.voice_id = voice_id

def get_voice_file(voice):
  
  char_id   = voice.char_id
  chapter   = voice.chapter
  voice_id  = voice.voice_id
  
  if voice_id < 0:
    return None
  
  if char_id in VOICE_OFFSETS and chapter in VOICE_OFFSETS[char_id]:
    
    # I have no idea why they wouldn't just give them their own section numbers.
    if chapter == CH_GEN:
      if voice_id > 800:
        chapter   = CH_GEN_5
        voice_id -= 800
      
      elif voice_id > 600:
        chapter   = CH_GEN_4
        voice_id -= 600
      
      elif voice_id > 400:
        chapter   = CH_GEN_3
        voice_id -= 400
      
      elif voice_id > 100:
        chapter   = CH_GEN_2
        voice_id -= 100
    
    offset = VOICE_OFFSETS[char_id][chapter]
    
    if offset < 0:
      return None
    
    return offset + voice_id
    
  else:
    return None

### EOF ###