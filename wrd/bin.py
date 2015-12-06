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

import bitstring
from bitstring import BitStream, ConstBitStream

from wrd.ops import *
from wrd.parser import parse_command, InvalidWrdHeader

################################################################################
### Converts binary wrd data to a list of commands which can be used in all
### the other functions in this module.
################################################################################
def from_bin(data):

  # Eat the header.
  parse_command(data)
  
  commands = []
  while True:
    try:
      op, params = parse_command(data)
      commands.append((op, params))
    
    except InvalidWrdHeader:
      byte = data.read("uint:8")
      commands.append((WRD_INVALID, {"val": byte}))
    
    except:
      break
  
  return commands

################################################################################
### Converts a list of commands to the binary format used by the game.
################################################################################
def to_bin(commands):

  data  = BitStream()
  lines = 0
  
  for op, params in commands:
    if op == WRD_HEADER:
      continue
    
    if not op in OP_PARAMS:
      # raise Exception("Unknown op: 0x%02X" % op)
      print "Unknown op: 0x%02X" % op
      continue
    
    param_info = OP_PARAMS[op]
    
    # If it has a custom parsing function, use the equivalent packing function.
    if isinstance(param_info, basestring):
      command = globals()[OP_FUNCTIONS[op]](**params)
      data.append(command)
    
    else:
      if op == WRD_SHOW_LINE:
        lines += 1
      
      data.append(bitstring.pack("uint:8, uint:8", CMD_MARKER, op))
      
      unnamed_param_id = 0
      
      for param_name, param_type in param_info:
        if param_name == None:
          data.append(bitstring.pack(param_type, params[param_name][unnamed_param_id]))
          unnamed_param_id += 1
          
        else:
          data.append(bitstring.pack(param_type, params[param_name]))
  
  return bitstring.pack("uint:8, uint:8, uintle:16", CMD_MARKER, WRD_HEADER, lines) + data

################################################################################
### Special function definitions.
################################################################################

def check_flag_a(flags, flag_ops, fail_label):
  # XX XX 00 YY 
  #   * If there are multiple flags (as many as needed)
  #   -> WW XX XX 00 YY 
  #
  #   * When all the flags have been listed.
  #   -> 70 3C 70 34 ZZ ZZ
  #
  #   * XX XX = Flag group/ID
  #   * YY = Flag State
  #     * 00 = Off
  #     * 01 = On
  #
  #   * WW = Operator
  #     * 06 = AND
  #     * 07 = OR  (?)
  #
  #   * ZZ ZZ = Label to jump to if check failed.
  
  command = bitstring.pack("uint:8, uint:8", CMD_MARKER, WRD_CHECKFLAG_A)
  
  for i, (flag_group, flag_id, flag_state) in enumerate(flags):
    command += bitstring.pack("uint:8, uint:8, uint:16", flag_group, flag_id, flag_state)
    
    if i < len(flag_ops):
      command += bitstring.pack("uint:8", flag_ops[i])
  
  command += bitstring.pack("uint:8, uint:8", CMD_MARKER, WRD_FLAG_CHECK_END)
  
  if not fail_label == None:
    command += bitstring.pack("uint:8, uint:8, uint:16", CMD_MARKER, WRD_GOTO_LABEL, fail_label)
  
  return command

def check_flag_b(flags, flag_ops, fail_label):

  command = bitstring.pack("uint:8, uint:8", CMD_MARKER, WRD_CHECKFLAG_B)
  
  for i, (unk1, unk2, unk3, unk4, unk5) in enumerate(flags):
    command += bitstring.pack("uint:8, uint:8, uint:8, uint:8, uint:8", unk1, unk2, unk3, unk4, unk5)
    
    if i < len(flag_ops):
      command += bitstring.pack("uint:8", flag_ops[i])
  
  command += bitstring.pack("uint:8, uint:8", CMD_MARKER, WRD_FLAG_CHECK_END)
  
  if not fail_label == None:
    command += bitstring.pack("uint:8, uint:8, uint:16", CMD_MARKER, WRD_GOTO_LABEL, fail_label)
  
  return command

def wait_frames(frames):
  return bitstring.pack("uint:8, uint:8", CMD_MARKER, WRD_WAIT_FRAME) * frames

def byte(val):
  return bitstring.pack("uint:8", val)

### EOF ###