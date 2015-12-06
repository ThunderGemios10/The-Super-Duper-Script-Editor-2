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

import codecs, os

def load_text(filename):
  if not os.path.isfile(filename):
    raise ValueError("%s is not a file." % filename)
  
  file = codecs.open(filename, mode = 'r', encoding = 'utf-16')
  text = file.read()
  file.close()
  return text
  
def save_text(text, filename):  
  file = codecs.open(filename, mode = 'w', encoding = 'utf-16le')
  file.write(text)
  file.close()

### EOF ###