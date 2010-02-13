#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# tab.py - tabing functional
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

from editor import Editor
#
# Tab class providing
#
class Tab(gtk.Notebook):
 
  def __init__(self):
    gtk.Notebook.__init__(self)
    self.set_property('homogeneous', True)
    pages = 1
  
  #
  #add new tab function
  #
  def new_tab(self):
      editor = Editor()
      scrolled_window = gtk.ScrolledWindow()
      
      self.add(scrolled_window)
      scrolled_window. add_with_viewport(editor)
 
      scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
      
      label = self.create_tab_label("New File",editor)
           
      self.set_tab_label_packing(scrolled_window,False,False,2)
      self.set_tab_label(scrolled_window,label)
 
      label.show_all()
 
      return editor
    
  #
  #create tab button close and label
  #
  def create_tab_label(self, title, tab_child):
      box = gtk.HBox()
      label = gtk.Label(title)
      closebtn = gtk.Button()
    
      image = gtk.Image()
      image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
   
      closebtn.set_image(image)
      closebtn.set_relief(gtk.RELIEF_NONE)

      box.pack_start(label, True, True)
      box.pack_end(closebtn, False, False)
    
      closebtn.connect("clicked",self.close_tab)
    
      return box 
  #
  #close tab
  #
  def close_tab(self,child):
  
      if self.get_n_pages() != self.get_current_page():
          self.set_current_page(self.get_n_pages())

      self.remove_page(self.get_current_page())
 
  
