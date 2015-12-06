################################################################################
### Copyright © 2012-2013 BlackDragonHunt
### Copyright © 2012-2013 /a/nonymous scanlations
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

from collections import OrderedDict
from wrd.ops import *

################################################################################
### CLASSES
################################################################################
class InvalidWrdHeader(Exception):
  pass

################################################################################
### Generic command parser.
################################################################################
def parse_command(data):
  
  header = data.peek("uint:8")
  
  if not header == CMD_MARKER:
    raise InvalidWrdHeader("Command 0x%02X does not begin with 0x%02X" % (header, CMD_MARKER))
  
  data.read("uint:8")
  op = data.read("uint:8")
  
  params = OrderedDict()
  
  if op in OP_PARAMS:
    param_info = OP_PARAMS[op]
    
    # If it's a custom function, use that.
    if isinstance(param_info, basestring):
      if param_info in globals():
        params = globals()[param_info](data)
      else:
        raise Exception("Function %s not defined." % param_info)
    
    # Otherwise, just use the param list.
    else:
      param_names = [info[0] for info in param_info]
      param_types = [info[1] for info in param_info]
      
      param_vals  = data.readlist(param_types)
      
      for name, val in zip(param_names, param_vals):
        
        if name == None:
          try:
            params[None].append(val)
          except:
            params[None] = [val]
        else:
          params[name] = val
  
  else:
    print "Unknown opcode encountered: 0x%02X" % op
    
  return op, params

################################################################################
### Custom command parsers.
################################################################################

########################################
### CONSTANTS
########################################
FLAG_OP_AND = 0x06
FLAG_OP_OR  = 0x07

FLAG_OPS    = [FLAG_OP_AND, FLAG_OP_OR]

def parse_checkflag_a(data):
  # 70 46 XX YY ZZ ZZ 
  #   * If there are multiple flags (as many as needed)
  #   -> WW XX YY ZZ ZZ 
  #
  #   * When all the flags have been listed.
  #   -> 70 3C 70 34 VV VV
  #
  #   * XX = Flag group
  #   * YY = Flag ID
  #   * ZZ ZZ = Flag State
  #     * 00 = Off
  #     * 01 = On
  #
  #   * WW = Operator
  #     * 06 = AND
  #     * 07 = OR  (?)
  #
  #   * VV VV = Label to jump to if check failed.
  
  flags = []
  flag_ops = []
  fail_label = None
  
  while True:
    flag_group  = data.read('uint:8')
    flag_id     = data.read('uint:8')
    flag_state  = data.read('uint:16')
    
    flags.append((flag_group, flag_id, flag_state))
    
    if data.peek('uint:8') in FLAG_OPS:
      flag_ops.append(data.read('uint:8'))
    else:
      break
  
  end_cmd  = data.readlist("uint:8, uint:8")
  if not end_cmd == [CMD_MARKER, WRD_FLAG_CHECK_END]:
    print "Invalid flag check. 0x%02X%02X" % tuple(end_cmd)
    return OrderedDict([("flags", flags), ("flag_ops", flag_ops), ("fail_label", fail_label)])
  
  if data.peeklist("uint:8, uint:8") == [CMD_MARKER, WRD_GOTO_LABEL]:
    data.read(16)
    fail_label = data.read('uint:16')
  
  return OrderedDict([("flags", flags), ("flag_ops", flag_ops), ("fail_label", fail_label)])

def parse_checkflag_b(data):
  # 70 47 XX XX XX XX XX
  #   * If there are multiple flags (as many as needed)
  #   -> WW XX XX XX XX XX
  #
  #   * When all the flags have been listed.
  #   -> 70 3C 70 34 ZZ ZZ
  #
  #   * XX XX XX XX XX = ???
  #
  #   * WW = Operator
  #     * 06 = AND
  #     * 07 = OR
  #
  #   * ZZ ZZ = Label to jump to if check failed.
  
  # Still not entirely sure what this does, but I've got a few ideas.
  # check_flag_b(flags = [(0, 13, 0, 0, 0)], flag_ops = [], fail_label = 504) -> Out of HP
  # check_flag_b(flags = [(0, 19, 0, 0, 2)], flag_ops = [], fail_label = 505) -> Difficulty: Hard
  
  flags = []
  flag_ops = []
  fail_label = None
  
  while True:
    flags.append(tuple(data.readlist(["uint:8"] * 5)))
    
    if data.peek('uint:8') in FLAG_OPS:
      flag_ops.append(data.read('uint:8'))
    else:
      break
  
  end_cmd = data.peeklist("uint:8, uint:8")
  if not end_cmd == [CMD_MARKER, WRD_FLAG_CHECK_END]:
    print "Invalid flag check. 0x%02X%02X" % tuple(end_cmd)
    return OrderedDict([("flags", flags), ("flag_ops", flag_ops), ("fail_label", fail_label)])
  data.read(16)
  
  if data.peeklist("uint:8, uint:8") == [CMD_MARKER, WRD_GOTO_LABEL]:
    data.read(16)
    fail_label = data.read('uint:16')
  
  return OrderedDict([("flags", flags), ("flag_ops", flag_ops), ("fail_label", fail_label)])

def parse_wait_frame(data):
  
  # If we're here, we already have one.
  frame_count = 1
  
  while data.peeklist("uint:8, uint:8") == [CMD_MARKER, WRD_WAIT_FRAME]:
    data.read(16)
    frame_count += 1
  
  return {"frames": frame_count}

### EOF ###