#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# sep.py - separator provide
# Copyright (C) Kuleshov Alexander 2010 <kuleshovmail@gmail.com>
# 
# main.py is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# main.py is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk

#
#menu and other separators provide
#
class SeparatorStruct(gtk.SeparatorMenuItem):
     
     #menu separators
     separator1 = gtk.SeparatorMenuItem()
     separator2 = gtk.SeparatorMenuItem()
     separator3 = gtk.SeparatorMenuItem()
     separator4 = gtk.SeparatorMenuItem()
     separator5 = gtk.SeparatorMenuItem()
     separator6 = gtk.SeparatorMenuItem()
     separator7 = gtk.SeparatorMenuItem()
 
     #toolbar separators
     separator8 = gtk.SeparatorToolItem()
     separator9 = gtk.SeparatorToolItem()
     separator10 = gtk.SeparatorToolItem()
     separator11 = gtk.SeparatorToolItem()

     def __init__(self):
         gtk.SeparatorMenuItem.__init__(self)
