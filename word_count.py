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

import re

RE_IGNORE = re.compile(ur"\<CLT.*?\>|<DIG.*?>|[\.\,\?\!\'\"…？！‘’“”【】]+", re.UNICODE | re.IGNORECASE)
RE_SEPS   = re.compile(ur"[―–—\n\s]+", re.UNICODE | re.IGNORECASE)

def count_words(text):
  text = RE_SEPS.sub(u" ", text)
  text = RE_IGNORE.sub(u"", text)
  return len(text.split())

### EOF ###