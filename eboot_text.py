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

from bitstring import ConstBitStream
import codecs
from csv import DictReader, DictWriter

import common

CSV_FILE = common.editor_config.eboot_text

class EbootText():
  def __init__(
    self,
    pos  = ConstBitStream(),
    orig = u"",
    text = u"",
    enc  = "UTF-8",
  ):
    self.pos  = pos
    self.orig = orig
    self.text = text
    self.enc  = enc

def get_eboot_text():
  
  eboot_csv = DictReader(open(CSV_FILE, 'rb'))
  
  eboot_text = []

  for row in eboot_csv:
    pos  = ConstBitStream(hex = row['Position'])
    orig = row['Orig'].decode("UTF-8")
    text = row['Text'].decode("UTF-8")
    enc  = row['Encoding'].decode("UTF-8")
    
    line = EbootText(pos, orig, text, enc)
    
    eboot_text.append(line)
  
  return eboot_text

def text_to_csv(eboot_text):
  
  eboot_csv = DictWriter(open(CSV_FILE, 'wb'), fieldnames = ['Position', 'Orig', 'Text', 'Encoding'])
  eboot_csv.writerow({'Position':'Position', 'Orig':'Orig', 'Text':'Text', 'Encoding':'Encoding'})
  
  for line in eboot_text:
    row = {}
    row['Position'] = line.pos.hex
    row['Orig']     = line.orig.encode("UTF-8")
    row['Text']     = line.text.encode("UTF-8")
    row['Encoding'] = line.enc.encode("UTF-8")
    
    eboot_csv.writerow(row)

### EOF ###