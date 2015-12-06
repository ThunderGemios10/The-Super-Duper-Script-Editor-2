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

import common
from scene_info import SceneInfo
from sprite import SpriteId, SPRITE_TYPE
from text_printer import IMG_FILTERS
from text_format import TEXT_FORMATS
from voice import VoiceId

from wrd.ops import *

##############################################################################
### Converts the parsed wrd file into a list of SceneInfo objects for use
### in the editor
##############################################################################
def to_scene_info(commands):
  
  cur_speaker   = 0x1F
  cur_sprite    = SpriteId()
  last_sprite   = -1
  cur_voice     = VoiceId()
  cur_bgm       = -1
  cur_trialcam  = None
  cur_sprite_obj  = None
  is_option     = False
  is_option_pt  = False
  option_val    = None
  show_tag      = True
  is_speaking   = True
  
  img_filter    = IMG_FILTERS.unfiltered
  
  cur_mode      = None
  cur_room      = -1
  
  check_obj     = -1
  check_char    = -1
  
  cur_ammo      = -1
  cur_cutin     = -1
  cur_present   = -1
  cur_bgd       = -1
  cur_flash     = -1
  cur_movie     = -1
  
  # Because we can put flashes on top of flashes.
  flash_stack   = []
  
  # If we set the speaker with a speaker tag,
  # don't let a voice file/sprite override it.
  speaker_set = False
  
  loaded_sprites = {}
  char_objects   = {}
  
  box_color = common.BOX_COLORS.yellow
  box_type  = common.BOX_TYPES.normal
  
  wrd_info = []
  
  for op, params in commands:
    
    ########################################
    ### Show line
    ########################################
    if op == WRD_SHOW_LINE or op == WRD_CALL_SCRIPT or op == WRD_GOTO_SCRIPT:
      scene_info = SceneInfo()
      
      if op == WRD_SHOW_LINE:
        scene_info.file_id = params["line"]
      
      else:
        scene_info.file_id    = None
        scene_info.goto_ch    = params["chapter"]
        scene_info.goto_scene = params["scene"]
        scene_info.goto_room  = params["room"]
      
      if not cur_mode == None:
        scene_info.mode = cur_mode
      
      scene_info.room = cur_room
      
      if not show_tag:
        scene_info.speaker = -1
      else:
        scene_info.speaker = cur_speaker
      
      scene_info.speaking   = is_speaking
      scene_info.sprite     = cur_sprite
      scene_info.voice      = cur_voice
      scene_info.bgm        = cur_bgm
      
      scene_info.box_color  = box_color
      scene_info.box_type   = box_type
      
      scene_info.ammo       = cur_ammo
      scene_info.bgd        = cur_bgd
      scene_info.cutin      = cur_cutin
      scene_info.present    = cur_present
      scene_info.flash      = cur_flash
      scene_info.movie      = cur_movie
      
      scene_info.img_filter = img_filter
      
      if not check_obj == -1:
        scene_info.special    = common.SCENE_SPECIAL.checkobj
        scene_info.extra_val  = check_obj
        # check_obj             = -1
        # check_char            = -1
      
      elif not check_char == -1:
        scene_info.special    = common.SCENE_SPECIAL.checkchar
        scene_info.extra_val  = (char_objects[check_char] if check_char in char_objects else "ID %d" % check_char)
        # check_obj             = -1
        # check_char            = -1
      
      if is_option:
        # scene_info.speaker    = -1
        scene_info.special    = common.SCENE_SPECIAL.option
        scene_info.extra_val  = option_val
      elif is_option_pt:
        scene_info.special    = common.SCENE_SPECIAL.showopt
        scene_info.extra_val  = option_val
      
      #scene_info.trialcam = cur_trialcam
      
      ##############################
      ### Reset stuff
      ##############################
      # cur_ammo = -1
      
      scene_info.headshot = cur_sprite_obj
      
      if is_option:
        is_option = False
        # option_val = None
      
      # is_option_pt = False
      speaker_set = False
      
      cur_voice = VoiceId()
      
      wrd_info.append(scene_info)
    
    ########################################
    ### Image filter
    ########################################
    elif op == WRD_FILTER_IMG:
      filter = params["filter"]
    
      if filter == 0x00:
        img_filter = IMG_FILTERS.unfiltered
      elif filter == 0x01:
        img_filter = IMG_FILTERS.sepia
      elif filter == 0x05:
        img_filter = IMG_FILTERS.inverted
      else:
        img_filter = IMG_FILTERS.unfiltered
    
    ########################################
    ### Play movie
    ########################################
    elif op == WRD_MOVIE:
    
      id    = params["id"]
      state = params["state"]
      
      # Clear everything first, since a new call takes
      # priority of display over an old call.
      cur_bgd   = -1
      cur_flash = -1
      cur_movie = -1
      
      if state == 1:
        cur_movie = id
    
    ########################################
    ### Show flash/cutin
    ########################################
    elif op == WRD_FLASH:
      # If id <  1000, then it's a flash event.
      # if id >= 1000, then it's ammo
      # if id >= 1500, then it's an ammo update
      # if id >= 2000, then it's a present
      # If id >= 3000, it's a cutin.
      id    = params["id"]
      state = params["state"]
    
      # An actual cutin.
      if id >= 3000:
        if state == 1:
          cur_cutin = id - 3000
        else:
          cur_cutin = -1
      
      elif id >= 2000:
        if state == 1:
          cur_present = id - 2000
        else:
          cur_present = -1
      
      elif id >= 1500:
        if state == 1:
          cur_ammo = id - 1500
        else:
          cur_ammo = -1
      
      elif id >= 1000:
        if state == 1:
          cur_ammo = id - 1000
        else:
          cur_ammo = -1
      
      # A flash event.
      elif id < 1000:
      
        # Clear other stuff first, since a new call takes
        # priority of display over an old call.
        cur_bgd   = -1
        cur_movie = -1
        
        # These flash IDs are special trial animations that kind of screw things up.
        invalid_flash = range(200, 245) + [2, 27, 246, 247]
        
        if state > 0 and (id not in invalid_flash):
          if id in flash_stack:
            flash_stack.remove(id)
          flash_stack.append(id)
        
        elif state == -1 and len(flash_stack) > 0:
          if id in flash_stack:
            flash_stack.remove(id)
          else:
            flash_stack.pop()
        
        if len(flash_stack) == 0:
          cur_flash = -1
        else:
          cur_flash = flash_stack[-1]
          cur_trialcam = None
          cur_sprite = SpriteId()
    
    ########################################
    ### Play a voice
    ########################################
    elif op == WRD_VOICE:
      char_id   = params["char_id"]
      chapter   = params["chapter"]
      voice_id  = params["voice_id"]
      
      cur_voice = VoiceId(char_id, chapter, voice_id)
      
      if not speaker_set:
        cur_speaker = char_id
    
    ########################################
    ### Play BGM
    ########################################
    elif op == WRD_BGM:
      id          = params["id"]
      transition  = params["transition"]
      
      cur_bgm = id
    
    ########################################
    ### Get/update/clear ammo
    ########################################
    elif op == WRD_SET_AMMO:
      # If ID == 0xFF & State == 0x00, clear all ammo from ElectroiD
      # State == 01: Add to ElectroiD
      # State == 02: Update info
      
      id    = params["id"]
      state = params["state"]
      
      # if state in [0x01, 0x02]:
        # cur_ammo = id
      # else:
        # cur_ammo = -1
    
    ########################################
    ### Move camera during Class Trial
    ########################################
    elif op == WRD_TRIAL_CAM:
      char_id = params["char_id"]
      motion  = params["motion"]
      
      cur_trialcam = char_id
      
      if not char_id in loaded_sprites:
        cur_sprite = SpriteId()
      else:
        cur_sprite = loaded_sprites[char_id]
    
    ########################################
    ### Load 3D map
    ########################################
    elif op == WRD_LOAD_MAP:
      room  = params["room"]
      state = params["state"]
      
      if state == 0:
        cur_room = room
        cur_mode = common.SCENE_MODES.normal
    
    ########################################
    ### 
    ########################################
    elif op == WRD_SPRITE:
      obj_id       = params["obj_id"]
      char_id      = params["char_id"]
      sprite_id    = params["sprite_id"]
      # 00 = Kill (?)
      # 01 = Show (?)
      # 03 = Fade out (?)
      # 04 = Hide (?)
      sprite_state = params["sprite_state"]
      sprite_type  = params["sprite_type"]
      
      cur_sprite_obj = obj_id
      
      if not obj_id in char_objects:
        char_objects[obj_id] = char_id
      
      sprite_info = SpriteId(SPRITE_TYPE.bustup, char_id, sprite_id)
      loaded_sprites[char_id] = sprite_info
      
      last_sprite = char_id
      
      # If we have a camera, that means we might not be showing a sprite
      # just because we loaded it. Wait for the camera flag to point at a sprite.
      if cur_trialcam == None:
        if sprite_state in [0x00, 0x03, 0x04, 0x05, 0x07, 0x0A, 0x10]:
          cur_sprite = SpriteId()
          continue
        # Kind of hackish. Sprites in 2D mode always seem to use obj_id 0 or 1,
        # but those IDs are also used in 3D mode, so I'm not sure how to tell
        # the difference between the two modes yet. So, we ignore any obj_id
        # greater than 1, because we don't care about the sprites in 3D.
        elif obj_id > 1:
          continue
        # Also kind of hackish. ID 98 is the "blank" model for characters
        # displayed in 3D, and sometimes, if the previous check misses when
        # the game is removing a character, it shows up as an "unknown" sprite.
        elif char_id == 98:
          cur_sprite = SpriteId()
          continue
        else:
          cur_sprite = sprite_info
      
      if not speaker_set:
        cur_speaker = char_id
    
    ########################################
    ### Set speaker tag
    ########################################
    elif op == WRD_SPEAKER:
      id = params["id"]
      
      # if id in common.CHAR_IDS:
      if id == 0x3E:
        if not speaker_set:
          cur_speaker = last_sprite
          speaker_set = True
      else:
        cur_speaker = id
        speaker_set = True
    
    ########################################
    ### 
    ########################################
    elif op == WRD_CHANGE_UI:
      # Element / State
      # 00 00 = "Speaking" window
      # 00 01 = "Thoughts" window
      # 01 00 = Hide text box (?)
      # 01 01 = Show text box (?)
      # 02 00 = Hide nametag (?)
      # 02 01 = Show nametag (?)
      # 03 00 = Orange box (?)
      # 03 01 = Green box (?)
      # 03 02 = Blue box (?)
      # 04 YY = ??
      # 06 YY = ??
      # 07 YY = ??
      # 09 YY = ??
      # 0B YY = ??
      # 0D 00 = Stop shaking
      # 0D 01 = Start shaking
      # 33 00 = Normal, round text box (?)
      # 33 01 = Flat, black overlay (?)
      element = params["element"]
      state   = params["state"]
      
      # Text box
      if element == 0x00:
        if state == 0x00:
          is_speaking = True
        elif state == 0x01:
          is_speaking = False
        
        show_tag = True
      
      # Text box
      elif element == 0x01:
        if state == 0x00:
          # Is it safe to assume that when we kill the text box
          # we are also killing any existing BGDs and the like?
          # cur_bgd   = -1
          # cur_cutin = -1
          # cur_flash = -1
          # cur_movie = -1
          # cur_ammo  = -1
          pass
      
      # Speaker tag
      # elif element == 0x02:
        # if state == 0x00:
          # show_tag = False
        # elif state == 0x01:
          # show_tag = True
      
      # Box type
      elif element == 0x33:
        if state == 0x00:
          box_type = common.BOX_TYPES.normal
        elif state == 0x01:
          box_type = common.BOX_TYPES.flat
    
    ########################################
    ### Check a person
    ########################################
    elif op == WRD_CHECK_CHAR:
      check_char  = params["id"]
      if check_char == 255:
        check_char = -1
      
      check_obj   = -1
    
    ########################################
    ### Check an object
    ########################################
    elif op == WRD_CHECK_OBJ:
      check_obj   = params["id"]
      if check_obj == 255:
        check_obj = -1
      check_char  = -1
    
    ########################################
    ### An options section
    ########################################
    elif op == WRD_CHOICE:
      # Option flag:
      # 01 = Choice ID (?)
      # 02 = Choice ID (?)
      # 03 = Choice ID (?)
      # 12 = Out of time (?)
      # 13 = Options prompt (?)
      # FF = End of options section (?)
      option_flag = params["flag"]
      
      if option_flag in [0x13, 0xFE]:
        is_option    = False
        is_option_pt = True
        option_val   = "Prompt"
      
      elif option_flag in [0x12, 0xFD]:
        is_option    = False
        is_option_pt = True
        option_val   = "Time Up"
      
      elif option_flag == 0xFF:
        is_option    = False
        is_option_pt = False
        
      elif option_flag < 0x10:
        is_option    = True
        is_option_pt = True
        option_val   = "Option %d" % option_flag
      
      elif option_flag == 0xFC:
        is_option    = False
        is_option_pt = True
        option_val   = "Generic Wrong"
      
      else:
        is_option    = False
        is_option_pt = True
        option_val   = "Unknown"
    
    ########################################
    ### Show a BGD
    ########################################
    elif op == WRD_BGD:
      id    = params["id"]
      state = params["state"]
      
      # Clear everything first, since a new call takes
      # priority of display over an old call.
      
      if state == 1:
        cur_bgd      = id
        cur_flash    = -1
        cur_movie    = -1
        cur_trialcam = None
        cur_sprite   = SpriteId()
      
      elif id == 65535 or id == -1:
        cur_bgd      = -1
        cur_flash    = -1
        cur_movie    = -1
      
      else:
        cur_bgd = -1
    
    ### if op == WRD_??? ###
  ### for op, params in commands ###
  
  if len(wrd_info) == 0:
    return None
  else:
    return wrd_info

### EOF ###