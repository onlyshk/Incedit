#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# toolbar.py - toolbar provide
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
import incedit
import sep

#
#class toolbar provide
#
class ToolBar(gtk.Toolbar):

     create_bar = gtk.ToolButton(gtk.STOCK_NEW)
     open_bar   = gtk.ToolButton(gtk.STOCK_OPEN)
     save_bar   = gtk.ToolButton(gtk.STOCK_SAVE)  
     print_bar  = gtk.ToolButton(gtk.STOCK_PRINT)
          
     def __init__(self):
         gtk.Toolbar.__init__(self)
  
     def init_toolbar(self):
         self.insert(self.create_bar,0)
         self.insert(self.open_bar,1)
         self.insert(self.save_bar,2)
         self.insert(sep.SeparatorStruct.separator8,3)
         self.insert(self.print_bar,4)
         self.insert(sep.SeparatorStruct.separator9,5)
       
         
 
