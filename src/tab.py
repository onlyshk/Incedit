#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tab.py - provide tab system and some standart operation with files
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
import utils
from incedit import Incedit
from editor import Editor

class Tab(gtk.Notebook):
 
  already_save = []
  saving = False
  editor = Editor()

  def __init__(self):
    gtk.Notebook.__init__(self)
    self.set_property('homogeneous', True)
    self.set_property('show-tabs', True) 
    self.set_scrollable(True)

  #
  #tab-label provide
  #
  def set_label(self,label):
      label = self.create_tab_label(label,self.editor)
      self.set_tab_label(self.get_nth_page(self.get_current_page()),label)
      label.show_all()
      self.show_all()

  # 
  #add new tab
  #
  def new_tab(self,label):
      self.editor = gtk.TextView()
      self.scrolled_window = gtk.ScrolledWindow()
      
      self.add(self.scrolled_window)

      self.scrolled_window.add_with_viewport(self.editor)
        
      self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
      
      label = self.create_tab_label(label,self.scrolled_window)

      self.set_tab_label_packing(self.scrolled_window,False,False,2)
      self.set_tab_label(self.scrolled_window,label)

      self.saving = False
      self.already_save.insert(self.get_current_page(),self.get_n_pages() - 1) 
      label.show_all()

      self.show_all()
      print self.already_save
      return self.editor

  #
  #create tab
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
 
      closebtn.connect("clicked", self.close_tab, tab_child)

      return box
    
  def save_as_file(self):
      
      dialog = gtk.FileChooserDialog("Save..",
                                     None,
                                     gtk.FILE_CHOOSER_ACTION_SAVE,
                                     (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                     gtk.STOCK_SAVE, gtk.RESPONSE_OK))
      
      txt_filter=gtk.FileFilter()
      txt_filter.set_name("Text files")
      txt_filter.add_mime_type("text/*")
      all_filter=gtk.FileFilter()
      all_filter.set_name("All files")
      all_filter.add_pattern("*")
     
      dialog.add_filter(txt_filter)
      dialog.add_filter(all_filter)

      response = dialog.run()
      file_name = dialog.get_filename()

      if file_name not in self.already_save:
         self.already_save.insert(self.get_current_page(),file_name) 
      if response == gtk.RESPONSE_OK:
          label = gtk.Label(file_name)

          textbuffer = self.editor.get_buffer()
  
          file_save = open(file_name,"w")  
          file_save.write(textbuffer.get_text(textbuffer.get_start_iter(),
                                              textbuffer.get_end_iter()))
        
          file_name = utils.cut_file_name(file_name)
          self.set_label(gtk.Label(file_name).get_text())

          file_save.close()                 
          self.show_all()
         
      elif response == gtk.RESPONSE_CANCEL:
          dialog.destroy()

      dialog.destroy()
      self.saving = True

      return file_name
  #
  #save file
  #
  def save_file(self):
      if self.saving == False:
         self.save_as_file()
      else:
         page = self.get_current_page()      
         name_of_file = self.already_save[page]
         textbuffer = self.editor.get_buffer()
         file = open(name_of_file,"w")
         file.write(textbuffer.get_text(textbuffer.get_start_iter(),
                                        textbuffer.get_end_iter()))
         file.close() 
         print Incedit.file_opened
  #
  #close file
  #
  def close_tab(self, widget, child):
    pagenum = self.page_num(child) 
    del self.already_save[pagenum - 1]
    self.remove_page(pagenum)
    self.saving = False
    print pagenum
   
  #
  #close all file
  #
  def close_all_tab(self,child):
     for child in self.get_children():
         self.remove(child)

