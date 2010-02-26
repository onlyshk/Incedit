# find.py - find in text
# Copyright (C) Kuleshov Alexander 2010 <kuleshovmail@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#  
#  You should have received a copy of the GNU Lesser General Public
#  License along with main.c;if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301,  USA

import gtk
 
import tab
import incedit

class Finder(gtk.Window):

     box = gtk.Table()
     fix = gtk.Fixed()

     def __init__(self):
         super(Finder, self).__init__()
         self.set_size_request(300,100)
         self.set_position(gtk.WIN_POS_CENTER)
         self.set_title("Find")
         self.set_modal(True)
         self.set_gravity(False)
         self.set_resizable(False)
         
         self.init_form()
           
         self.add(self.fix)
         self.show_all()

     def init_form(self):
         
          self.close_button = gtk.Button("Close",gtk.STOCK_CLOSE)
          self.find_button  = gtk.Button("Find",gtk.STOCK_FIND)
          self.close_button.set_size_request(90,30)
          self.find_button.set_size_request(90,30)
          
          self.text_find    = gtk.Entry()
          self.text_find.set_size_request(280,25)

          self.label        = gtk.Label("Enter text to search")

          self.fix.put(self.label,13,8)
          self.fix.put(self.text_find,10,30)
          self.fix.put(self.find_button,10,63)
          self.fix.put(self.close_button,200,63)

          self.close_button.connect("clicked",self.close)
          self.find_button.connect("clicked",self.find)

     def close(self,widget):
         self.destroy()

     
     def find(self,widget):
         text_for_find = self.text_find.get_text()
         tab.Tab.find()

   
