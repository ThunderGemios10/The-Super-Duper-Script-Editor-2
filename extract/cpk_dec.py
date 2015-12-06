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

from bitstring import ConstBitStream, BitArray
import os
import time

from ctypes import byref, cast, cdll, create_string_buffer, c_long, c_char, POINTER
cpk_decompress = cdll.LoadLibrary('extract/cpk_uncompress.dll')

############################################################
### CONSTANTS
############################################################
CRILAYLA_MAGIC = ConstBitStream(hex = "0x4352494C41594C41") # "CRILAYLA"

VLE_LEVELS = 4
VLE_LENS   = [2, 3, 5, 8]

############################################################
### VARIABLES
############################################################
__offset    = 0
__bit_pool  = 0
__bits_left = 0
__data      = bytes()

############################################################
### FUNCTIONS
############################################################

##################################################
### 
##################################################
def decompress_cpk_dll(data, extract_size):
  
  in_data   = create_string_buffer(data.bytes)
  out_data  = create_string_buffer(extract_size)
  
  length = cpk_decompress.CPK_uncompress(byref(in_data), data.len / 8, byref(out_data), extract_size)
  out_data = ConstBitStream(bytes = out_data)
  
  return out_data

def decompress_cpk_dll2(data, extract_size):
  
  in_data   = create_string_buffer(data.bytes)
  length    = c_long(0)
  
  out_data_ptr = cpk_decompress.uncompress(byref(in_data), 0, data.len / 8, byref(length))
  out_data_ptr = cast(out_data_ptr, POINTER(c_char))
  length = length.value
  
  out_data = out_data_ptr[:length]
  out_data = ConstBitStream(bytes = out_data)
  
  cpk_decompress.free_buffer(out_data_ptr)
  
  return out_data

##################################################
### 
##################################################
def __get_next_bits(bit_count):
  global __offset
  global __bit_pool
  global __bits_left
  global __data
  #offset    = __offset
  #bit_pool  = __bit_pool
  #bits_left = __bits_left
  data      = __data
  
  out_bits = 0
  bits_produced = 0
  
  while (bits_produced < bit_count):
    if __bits_left == 0:
      __bit_pool = ord(data[__offset])
      __bits_left = 8
      __offset -= 1
    
    bits_this_round = 0
    if __bits_left > (bit_count - bits_produced):
      bits_this_round = bit_count - bits_produced
    else:
      bits_this_round = __bits_left
    
    out_bits <<= bits_this_round
    out_bits |= (__bit_pool >> (__bits_left - bits_this_round)) & ((1 << bits_this_round) - 1)
    
    __bits_left -= bits_this_round
    bits_produced += bits_this_round
  
  #__offset    = offset
  #__bit_pool  = bit_pool
  #__bits_left = bits_left
  return out_bits

##################################################
### 
##################################################
def decompress_cpk_py(data, extract_size):
  global __offset
  global __bit_pool
  global __bits_left
  global __data
  
  data.pos = 0
  magic = data.read(64)
  
  if not magic == CRILAYLA_MAGIC or magic.uintle == 0:
    print "Didn't find 0 or CRILAYLA signature for compressed data."
    return data
  
  uncompressed_size          = data.read("uintle:32")
  uncompressed_header_offset = data.read("uintle:32") + 0x10
  
  if uncompressed_header_offset + 0x100 != data.len / 8:
    print "Size mismatch."
    return data
  
  __data = data.bytes
  
  #uncompressed_header = data[uncompressed_header_offset * 8 : (uncompressed_header_offset + 0x100) * 8]
  uncompressed_header = __data[uncompressed_header_offset : uncompressed_header_offset + 0x100]
  out_data = bytearray(uncompressed_size + 0x100)
  out_data[:0x100] = uncompressed_header
  
  __offset     = len(__data) - 0x100 - 1
  __bit_pool   = 0
  __bits_left  = 0
  output_end   = 0x100 + uncompressed_size - 1
  bytes_output = 0
  
  while bytes_output < uncompressed_size:
  
    if __get_next_bits(1):
      backref_offset = output_end - bytes_output + __get_next_bits(13) + 3
      backref_length = 3
      
      # Says "decode variable length coding for length"
      # in the original C, but I dunno what that means.
      vle_level  = 0
      
      for i in xrange(VLE_LEVELS):
        this_level = __get_next_bits(VLE_LENS[vle_level])
        backref_length += this_level
        
        if this_level != ((1 << VLE_LENS[vle_level]) - 1):
          break
        
        vle_level += 1
      
      if vle_level == VLE_LEVELS:
        this_level == 255
        while this_level == 255:
          this_level = __get_next_bits(8)
          backref_length += this_level
      
      for i in xrange(backref_length):
        out_data[output_end - bytes_output] = out_data[backref_offset]
        
        backref_offset -= 1
        bytes_output   += 1
    
    else:
      # Verbatim byte.
      out_data[output_end - bytes_output] = __get_next_bits(8)
      bytes_output += 1
  
  # while bytes_output < uncompressed_size
  
  return ConstBitStream(bytes = out_data)

decompress_cpk = decompress_cpk_dll
#decompress_cpk = decompress_cpk_py

##################################################
### 
##################################################
if __name__ == "__main__":
  import sys
  from cpk_ex import dump_to_file
  
  to_dec = "bin_anagram2.pak"
  
  if len(sys.argv) > 1:
    to_dec = sys.argv[1].decode(sys.stdin.encoding)
  data = ConstBitStream(filename = to_dec)
  out_data = decompress_cpk(data)
  
  out_name, out_ext = os.path.splitext(to_dec)
  out_name = out_name + "-out" + out_ext
  
  dump_to_file(out_data, out_name)

### EOF ###