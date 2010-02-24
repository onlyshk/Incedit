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
# WITHOUT ANY WARRANTY; without esavingven the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 
 
import gtk 
import utils
import pango
from incedit import Incedit
import undostack

class Tab(gtk.Notebook):
 
  already_save = []
  editor = gtk.TextView()

  undo_pool = []
  

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
 
      self.already_save.append(self.get_current_page()) 
      label.show_all()
         
      self.editor.modify_font(pango.FontDescription("Monospace 12"))

      self.show_all()
 
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
  
  #
  #save as file
  #
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
 
      return file_name
  #
  #save file
  #
  def save_file(self): 
      hbox = self.get_tab_label(self.get_nth_page(self.get_current_page()))
      label_of_tab = hbox.get_children()
      text_of_tab = label_of_tab[0].get_text()
 
      if  text_of_tab == "New File":
         self.save_as_file() 
      else:
         page = self.get_current_page()      
         name_of_file = self.already_save[page]
         textbuffer = self.editor.get_buffer()
 
         file = open(name_of_file,"w")
         file.write(textbuffer.get_text(textbuffer.get_start_iter(),
                                        textbuffer.get_end_iter()))
         file.close() 
 
         hbox = None
         
  #
  #close file
  #
  def close_tab(self,widget,child):    
      dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                 gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,"Do you want to save file?")
      dialog.set_title("Close file!")
      response = dialog.run()
        
      if response == gtk.RESPONSE_YES:
          dialog.destroy()
          self.save_as_file()
  
          pagenum = self.page_num(child) 
          del self.already_save[pagenum]
 
          self.remove_page(pagenum)
      else: 
          dialog.destroy()
          
          pagenum = self.page_num(child) 
          del self.already_save[pagenum]
 
          self.remove_page(pagenum)

  #
  #copy/paste/cut
  #
  def copy_buffer(self):
      self.editor.emit("copy_clipboard")
  def cut_buffer(self):
      self.editor.emit("cut_clipboard")
  def paste_buffer(self):
      self.editor.emit("paste_clipboard")

  #
  #delete text provide
  #
  def delete_buffer(self):  
      textbuffer = self.editor.get_buffer()    
      if textbuffer.get_has_selection() == False:
         pass
      else:
         textbuffer.delete_selection(True, True)

  #
  #select all provide
  #
  def select_all(self):
      textbuffer = self.editor.get_buffer()
      textbuffer.place_cursor(textbuffer.get_end_iter())
      textbuffer.move_mark(textbuffer.get_mark("selection_bound"),textbuffer.get_start_iter())

  def undo(self): 
      textbuffer = self.editor.get_buffer()

  def redo(self):
      pass

