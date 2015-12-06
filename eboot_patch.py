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

from bitstring import ConstBitStream, BitStream
# from enum import Enum

import common
import clt

NAME    = "name"
ENABLED = "enabled"
CFG_ID  = "cfg_id"
DATA    = "data"
POS     = "pos"
ORIG    = "orig"
PATCH   = "patch"

# LANGUAGES   = [u"Japanese", u"English", u"French", u"Spanish", u"German", u"Italian", u"Dutch", u"Portuguese", u"Russian", u"Korean", u"Traditional Chinese", u"Simplified Chinese"]
LANGUAGES   = [u"日本語", u"English", u"Français", u"Español", u"Deutsch", u"Italiano", u"Nederlands", u"Português", u"Русский", u"한국어", u"繁體中文", u"简体中文"]
LANG_CFG_ID = "sys_menu_lang"
CLT_CFG_ID  = "custom_clt"

EBOOT_PATCHES = [
  {NAME: "Extend EBOOT", ENABLED: True, CFG_ID: None, DATA:
    [
      {POS: 0x0000002C, ORIG: ConstBitStream(hex = "0x0300"), PATCH: ConstBitStream(hex = "0x0400")},
      {POS: 0x00000054, ORIG: ConstBitStream(hex = "0x0100000040CB200080CA20000000000028E40000842A2E000600000040000000"), PATCH: ConstBitStream(hex = "0x0100000040CB200020F54E000000000000200100002001000700000010000000")},
      {POS: 0x00000074, ORIG: ConstBitStream(hex = "0xA000007070AF21000000000000000000D8560D000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0x0100000040EB210080CA20000000000028E40000842A2E000600000040000000A000007070CF22000000000000000000D8560D00000000000000000010000000")},
    ]
  },
  {NAME: "Game Button Order", ENABLED: True, CFG_ID: "01_game_btn", DATA:
    [
      {POS: 0x0007A4C8, ORIG: ConstBitStream(hex = "0x0400B18F"), PATCH: ConstBitStream(hex = "0x48CD330A")},
      {POS: 0x0020CB40, ORIG: ConstBitStream(hex = "0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0x0400B18F21202002002025320200A014004031360040313A0040843002008014002031360020313A03F9210A00000000")},
    ]
  },
  {NAME: "Home/Save Button Order", ENABLED: True, CFG_ID: "03_home_btn", DATA:
    [
      {POS: 0x0008CCF8, ORIG: ConstBitStream(hex = "0x21108000"), PATCH: ConstBitStream(hex = "0x01000224")},
    ]
  },
  {NAME: "Fix Error Code 80020148", ENABLED: True, CFG_ID: "04_fix_80020148", DATA:
    [
      {POS: 0x00000004, ORIG: ConstBitStream(hex = "0x00"), PATCH: ConstBitStream(hex = "0x01")},
      {POS: 0x00000007, ORIG: ConstBitStream(hex = "0x01"), PATCH: ConstBitStream(hex = "0x00")},
    ]
  },
  {NAME: "Increase Dialog Line Limit to 96 Characters", ENABLED: True, CFG_ID: "05_dialog_line_96", DATA:
    [
      # Move current line buffer: raw addresses (0x08CAF3C6 -> 0x08CF3550)
      {POS: 0x000CB528, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000CB534, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000D1BD0, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000D1BD4, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000D25D8, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000D25DC, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000D962C, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000D9638, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000D963C, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000DB820, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000DB824, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000DB828, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000DB82C, ORIG: ConstBitStream(hex = "0x26EA"), PATCH: ConstBitStream(hex = "0xD02D")},
      {POS: 0x000DB95C, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000DB960, ORIG: ConstBitStream(hex = "0x26EA"), PATCH: ConstBitStream(hex = "0xD02D")},
      {POS: 0x000DB96C, ORIG: ConstBitStream(hex = "0x3800"), PATCH: ConstBitStream(hex = "0xC000")},
      {POS: 0x000DCFE0, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000DCFEC, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000DE5E8, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000DE5F4, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000DE92C, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000DE938, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000DE93C, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000FF1DC, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000FF230, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000FF1E4, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000FF2D0, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000FF2D8, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000FFD34, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000FFD38, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x000FFE44, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x000FFE48, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x001000B0, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x00100430, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x00100598, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x0010059C, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      {POS: 0x00100724, ORIG: ConstBitStream(hex = "0x2A00"), PATCH: ConstBitStream(hex = "0x2E00")},
      {POS: 0x0010072C, ORIG: ConstBitStream(hex = "0x46E9"), PATCH: ConstBitStream(hex = "0xD02A")},
      # Move current line buffer: relative addresses
      {POS: 0x0020CFF0, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08043CEA3284240800E00321104400")},
      {POS: 0x000CE600, ORIG: ConstBitStream(hex = "0x4010050021104800"), PATCH: ConstBitStream(hex = "0x74CE330E40100500")},
      {POS: 0x0020D000, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08073CEA32E7240800E00321104700")},
      {POS: 0x000CE754, ORIG: ConstBitStream(hex = "0x4010060021104800"), PATCH: ConstBitStream(hex = "0x78CE330E40100600")},
      {POS: 0x0020D010, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08043CEA3284240800E00321186400")},
      {POS: 0x000CE7EC, ORIG: ConstBitStream(hex = "0x40180A0021187E00"), PATCH: ConstBitStream(hex = "0x7CCE330E40180A00")},
      {POS: 0x0020D020, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08033CEA3263240800E00321104300")},
      {POS: 0x000CE9C4, ORIG: ConstBitStream(hex = "0x4010040021105000"), PATCH: ConstBitStream(hex = "0x80CE330E40100400")},
      {POS: 0x0020D030, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08073CEA32E7240800E00321104700")},
      {POS: 0x000CEA84, ORIG: ConstBitStream(hex = "0x4010060021105000"), PATCH: ConstBitStream(hex = "0x84CE330E40100600")},
      {POS: 0x0020D040, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08043CEA3284240800E00321186400")},
      {POS: 0x000CEB10, ORIG: ConstBitStream(hex = "0x40180A0021187100"), PATCH: ConstBitStream(hex = "0x88CE330E40180A00")},
      {POS: 0x000CE974, ORIG: ConstBitStream(hex = "0x6602A2940001422C"), PATCH: ConstBitStream(hex = "0x8CCE330E00000000")},
      {POS: 0x0020D050, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08023C503542940800E0030001422C")},
      # Move current line CLT buffer: relative addreses
      {POS: 0x0020D060, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08073C0A35E7240800E00321504701")},
      {POS: 0x000CE7F4, ORIG: ConstBitStream(hex = "0x2310470021505E01"), PATCH: ConstBitStream(hex = "0x90CE330E23104700")},
      {POS: 0x0020D070, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08073C0A35E7240800E00321504701")},
      {POS: 0x000CEB18, ORIG: ConstBitStream(hex = "0x2310470021505101"), PATCH: ConstBitStream(hex = "0x94CE330E23104700")},
      # Move current line CLT buffer: load
      {POS: 0x0020D080, ORIG: ConstBitStream(hex = "0x0000000000000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF08083C50380825214006010800E00300000891")},
      {POS: 0x000CEB88, ORIG: ConstBitStream(hex = "0x1900970021107000BA030586BC03068646034890"), PATCH: ConstBitStream(hex = "0x98CE330E1900970021107000BA030586BC030686")},
      {POS: 0x000CEBC0, ORIG: ConstBitStream(hex = "0x1900920021107000BA030586BC03068646034890"), PATCH: ConstBitStream(hex = "0x98CE330E1900920021107000BA030586BC030686")},
      {POS: 0x000CEC04, ORIG: ConstBitStream(hex = "0x2110C800BA030585BC03068546034890"), PATCH: ConstBitStream(hex = "0x98CE330E2110C800BA030585BC030685")},
      {POS: 0x000CEC30, ORIG: ConstBitStream(hex = "0xBA030586BC03068646034890"), PATCH: ConstBitStream(hex = "0x98CE330EBA030586BC030686")},
      # Move current line buffer and current line CLT buffer: 0xDB91C
      {POS: 0x000DB9DC, ORIG: ConstBitStream(hex = "0x40100B0021104500"), PATCH: ConstBitStream(hex = "0xA0CE330E40100B00")},
      {POS: 0x000DB9E4, ORIG: ConstBitStream(hex = "0x21186501"), PATCH: ConstBitStream(hex = "0x00000000")},
      {POS: 0x0020D0A0, ORIG: ConstBitStream(hex = "0x00000000000000000000000000000000000000000000000000000000"), PATCH: ConstBitStream(hex = "0xCF080A3CEA324A2521104A00CF080A3C0A354A250800E00321186A01")},
      # Reducing backlog length from 512 lines to 144 lines
      {POS: 0x000CECA4, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x000CECB0, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x000CECB8, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x000CEEB0, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x000CEEF8, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x000DBAA8, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x000DBAD0, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x000DBAD4, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x000DBAF8, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x0016814C, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      {POS: 0x0016819C, ORIG: ConstBitStream(hex = "0x0002"), PATCH: ConstBitStream(hex = "0x9000")},
      # Change line length: 28 -> 96
      {POS: 0x000CED00, ORIG: ConstBitStream(hex = "0x1C00"), PATCH: ConstBitStream(hex = "0x6000")},
      {POS: 0x000CEDFC, ORIG: ConstBitStream(hex = "0x1C00"), PATCH: ConstBitStream(hex = "0x6000")},
      {POS: 0x000D7CA0, ORIG: ConstBitStream(hex = "0x1C00"), PATCH: ConstBitStream(hex = "0x6000")},
      {POS: 0x000D8B7C, ORIG: ConstBitStream(hex = "0x1C00"), PATCH: ConstBitStream(hex = "0x6000")},
      {POS: 0x000D90C4, ORIG: ConstBitStream(hex = "0x1C00"), PATCH: ConstBitStream(hex = "0x6000")},
      {POS: 0x000DB830, ORIG: ConstBitStream(hex = "0x1C00"), PATCH: ConstBitStream(hex = "0x6000")},
      {POS: 0x000DB9B0, ORIG: ConstBitStream(hex = "0x1C00"), PATCH: ConstBitStream(hex = "0x6000")},
      {POS: 0x000DBA5C, ORIG: ConstBitStream(hex = "0x1C00"), PATCH: ConstBitStream(hex = "0x6000")},
      {POS: 0x000DBAC0, ORIG: ConstBitStream(hex = "0x1C00"), PATCH: ConstBitStream(hex = "0x6000")},
      # Change line length: 84 -> 288
      {POS: 0x000CE8D8, ORIG: ConstBitStream(hex = "0x5400"), PATCH: ConstBitStream(hex = "0x2001")},
      # Change line length: 112 -> 384
      {POS: 0x000CE5E0, ORIG: ConstBitStream(hex = "0x7000"), PATCH: ConstBitStream(hex = "0x8001")},
      {POS: 0x000CE618, ORIG: ConstBitStream(hex = "0x7000"), PATCH: ConstBitStream(hex = "0x8001")},
      {POS: 0x000CE6BC, ORIG: ConstBitStream(hex = "0x7000"), PATCH: ConstBitStream(hex = "0x8001")},
      {POS: 0x000CE8CC, ORIG: ConstBitStream(hex = "0x7000"), PATCH: ConstBitStream(hex = "0x8001")},
      {POS: 0x000CE8F0, ORIG: ConstBitStream(hex = "0x7000"), PATCH: ConstBitStream(hex = "0x8001")},
      {POS: 0x000CE9DC, ORIG: ConstBitStream(hex = "0x7000"), PATCH: ConstBitStream(hex = "0x8001")},
      {POS: 0x000CE9F8, ORIG: ConstBitStream(hex = "0x7000"), PATCH: ConstBitStream(hex = "0x8001")},
      {POS: 0x000CEB68, ORIG: ConstBitStream(hex = "0x7000"), PATCH: ConstBitStream(hex = "0x8001")},
      {POS: 0x000D2410, ORIG: ConstBitStream(hex = "0x7000"), PATCH: ConstBitStream(hex = "0x8001")},
      # Change line length: 224 -> 768
      {POS: 0x000CB53C, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000CFEB8, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000D1BDC, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000D25E8, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000D7C94, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000D8B70, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000D9644, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000DCFF4, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000DE5FC, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000DE944, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000FF1F0, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000FF2DC, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000FFD44, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x000FFE50, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x0010043C, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x001005AC, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      {POS: 0x00100734, ORIG: ConstBitStream(hex = "0xE000"), PATCH: ConstBitStream(hex = "0x0003")},
      # Change line length: sll ... 2 -> sll ... 5
      {POS: 0x000CE720, ORIG: ConstBitStream(hex = "0x80100900"), PATCH: ConstBitStream(hex = "0x40110900")},
      {POS: 0x000CE934, ORIG: ConstBitStream(hex = "0x80200300"), PATCH: ConstBitStream(hex = "0x40210300")},
      {POS: 0x000CEA1C, ORIG: ConstBitStream(hex = "0x80100500"), PATCH: ConstBitStream(hex = "0x40110500")},
      {POS: 0x000CEA54, ORIG: ConstBitStream(hex = "0x80100900"), PATCH: ConstBitStream(hex = "0x40110900")},
      {POS: 0x000CED08, ORIG: ConstBitStream(hex = "0x80180300"), PATCH: ConstBitStream(hex = "0x40190300")},
      {POS: 0x000CED40, ORIG: ConstBitStream(hex = "0x80180300"), PATCH: ConstBitStream(hex = "0x40190300")},
      {POS: 0x000CEDB4, ORIG: ConstBitStream(hex = "0x80180300"), PATCH: ConstBitStream(hex = "0x40190300")},
      {POS: 0x000CEE04, ORIG: ConstBitStream(hex = "0x80180300"), PATCH: ConstBitStream(hex = "0x40190300")},
      {POS: 0x000CEE40, ORIG: ConstBitStream(hex = "0x80180900"), PATCH: ConstBitStream(hex = "0x40190900")},
      {POS: 0x000DB9B8, ORIG: ConstBitStream(hex = "0x80180300"), PATCH: ConstBitStream(hex = "0x40190300")},
      {POS: 0x000DBA08, ORIG: ConstBitStream(hex = "0x80180300"), PATCH: ConstBitStream(hex = "0x40190300")},
      {POS: 0x000DBA3C, ORIG: ConstBitStream(hex = "0x80180300"), PATCH: ConstBitStream(hex = "0x40190300")},
      {POS: 0x000DBD48, ORIG: ConstBitStream(hex = "0x80180300"), PATCH: ConstBitStream(hex = "0x40190300")},
      # Change line length: sll ... 5 -> sll ... 7
      {POS: 0x000CE724, ORIG: ConstBitStream(hex = "0x40190900"), PATCH: ConstBitStream(hex = "0xC0190900")},
      {POS: 0x000CE938, ORIG: ConstBitStream(hex = "0x40110300"), PATCH: ConstBitStream(hex = "0xC0110300")},
      {POS: 0x000CEA20, ORIG: ConstBitStream(hex = "0x40190500"), PATCH: ConstBitStream(hex = "0xC0190500")},
      {POS: 0x000CEA58, ORIG: ConstBitStream(hex = "0x40190900"), PATCH: ConstBitStream(hex = "0xC0190900")},
      {POS: 0x000CED04, ORIG: ConstBitStream(hex = "0x40110300"), PATCH: ConstBitStream(hex = "0xC0110300")},
      {POS: 0x000CED3C, ORIG: ConstBitStream(hex = "0x40210300"), PATCH: ConstBitStream(hex = "0xC0210300")},
      {POS: 0x000CEDB0, ORIG: ConstBitStream(hex = "0x40210300"), PATCH: ConstBitStream(hex = "0xC0210300")},
      {POS: 0x000CEE00, ORIG: ConstBitStream(hex = "0x40110300"), PATCH: ConstBitStream(hex = "0xC0110300")},
      {POS: 0x000CEE44, ORIG: ConstBitStream(hex = "0x40110900"), PATCH: ConstBitStream(hex = "0xC0110900")},
      {POS: 0x000DB9B4, ORIG: ConstBitStream(hex = "0x40110300"), PATCH: ConstBitStream(hex = "0xC0110300")},
      {POS: 0x000DBA04, ORIG: ConstBitStream(hex = "0x40210300"), PATCH: ConstBitStream(hex = "0xC0210300")},
      {POS: 0x000DBA38, ORIG: ConstBitStream(hex = "0x40110300"), PATCH: ConstBitStream(hex = "0xC0110300")},
      {POS: 0x000DBD44, ORIG: ConstBitStream(hex = "0x40110300"), PATCH: ConstBitStream(hex = "0xC0110300")},
      # Change line length: divisor 0x24924925 -> 0x0AAAAAAB
      {POS: 0x001FA5CC, ORIG: ConstBitStream(hex = "0x25499224"), PATCH: ConstBitStream(hex = "0xABAAAA0A")},
      {POS: 0x000CE998, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x000D8378, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x000E69E4, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x000FBAB8, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x001673F0, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x00167748, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x001677D0, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x00167910, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x00174610, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x0017F720, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x0017FDA8, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x001800EC, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x00180460, ORIG: ConstBitStream(hex = "0x9224"), PATCH: ConstBitStream(hex = "0xAA0A")},
      {POS: 0x000CE99C, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x000D837C, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x000E69E8, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x000FBABC, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x001673F4, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x0016774C, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x001677D8, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x00167918, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x00174618, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x0017F728, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x0017FDB0, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x001800F8, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
      {POS: 0x0018046C, ORIG: ConstBitStream(hex = "0x2549"), PATCH: ConstBitStream(hex = "0xABAA")},
    ]
  },
  {NAME: "Custom CLT", ENABLED: True, CFG_ID: CLT_CFG_ID, DATA: []},
]

def apply_sys_lang(eboot):
  
  if LANG_CFG_ID in common.editor_config.hacks:
    sys_menu_lang = common.editor_config.hacks[LANG_CFG_ID]
  else:
    sys_menu_lang = 1
    common.editor_config.hacks[LANG_CFG_ID] = sys_menu_lang
  
  patch_loc = 0x0008C2FC
  patch = ConstBitStream(uintle = sys_menu_lang, length = 8) + ConstBitStream(hex = "0x000224")
  eboot.overwrite(patch, patch_loc * 8)
  
  return eboot

def apply_clt_patch(eboot):
  
  if common.editor_config.hacks[CLT_CFG_ID]:
    styles = clt.CLT_STYLES
  else:
    styles = clt.CLT_ORIGINAL
  
  patch_loc = 0x207288
  for i in sorted(styles.keys()):
    if i > clt.MAX_CLT:
      break
    
    patch = styles[i].to_bin()
    eboot.overwrite(patch, (patch_loc + (i * 0x10)) * 8)
  
  return eboot

def extend_eboot(eboot):
  
  NEW_SECTION_POS     = 0x20CB40
  NEW_SECTION_SIZE    = 73728
  
  ORIG_SIZE           = 3081800
  EXTENDED_SIZE       = ORIG_SIZE + NEW_SECTION_SIZE
  
  # Already extended, don't need to do it again.
  if eboot.len / 8 == EXTENDED_SIZE:
    return eboot
  elif eboot.len / 8 != ORIG_SIZE:
    raise ValueError("EBOOT neither matches original nor extended size. Try restoring the original, decrypted EBOOT.BIN to PSP_GAME/SYSDIR, then repack everything.")
  
  eboot.insert(BitStream(length = NEW_SECTION_SIZE * 8),   NEW_SECTION_POS * 8)
  
  # Since we're adding another program segment between program segments 0 and 1,
  # we need to update references to program segment 1 on the relocation table
  # so that they point to program segment 2.
  #
  # The pseudocode for this step is:
  # 
  # For b = every 8 bytes from 0x22CF70 to the end of the file:
  #   If b[5] == 1, replace it with 2.
  #   If b[6] == 1, replace it with 2.
  TABLE_START = 0x22CF70
  eboot.bytepos = TABLE_START
  
  while True:
    
    eboot.bytepos += 5
    
    if eboot.peek(8) == "0x01":
      eboot.overwrite("0x02")
    else:
      eboot.bytepos += 1
    
    if eboot.peek(8) == "0x01":
      eboot.overwrite("0x02")
    else:
      eboot.bytepos += 1
    
    eboot.bytepos += 1
    
    if eboot.bytepos >= eboot.len / 8:
      break
  
  return eboot

def apply_eboot_patches(eboot):
  
  eboot = extend_eboot(eboot)
  
  for patch in EBOOT_PATCHES:
  
    enabled = patch[ENABLED]
    if patch[CFG_ID] and patch[CFG_ID] in common.editor_config.hacks:
      enabled = common.editor_config.hacks[patch[CFG_ID]]
    
    # So we can undo patches if they've already been applied.
    key = PATCH if enabled else ORIG
    
    for item in patch[DATA]:
      eboot.overwrite(item[key], item[POS] * 8)
  
  eboot = apply_sys_lang(eboot)
  eboot = apply_clt_patch(eboot)
  
  return eboot

if __name__ == "__main__":
  src = "Y:\\Danganronpa\\Danganronpa2\\EBOOT-DEC.BIN"
  dst = "Y:\\Danganronpa\\Danganronpa2\\EBOOT-TEST.BIN"
  
  test = BitStream(filename = src)
  test = apply_eboot_patches(test)
  
  with open(dst, "wb") as f:
    test.tofile(f)

### EOF ###