#!/usr/bin/env python
 
 
import gtk 
import utils
from incedit import Incedit
from editor import Editor

class Tab(gtk.Notebook):
 
  already_save = []
  saving = False

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
      self.set_tab_label_packing(self.scrolled_window,False,False,2)
      self.set_tab_label(self.scrolled_window,label)
      label.show_all()

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

      return self.editor
 
  def create_tab_label(self, title, tab_child):
    box = gtk.HBox()
    icon = gtk.Image()
    icon.set_from_stock(title, gtk.ICON_SIZE_MENU)
    label = gtk.Label(title)
    closebtn = gtk.Button()
    image = gtk.Image()
    image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
    closebtn.connect("clicked", self.close_tab, tab_child)
    closebtn.set_image(image)
    closebtn.set_relief(gtk.RELIEF_NONE)
    box.pack_start(icon, False, False)
    box.pack_start(label, True, True)
    box.pack_end(closebtn, False, False)
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

          file_save = open(file_name,"w")
          
          textbuffer = self.editor.get_buffer()
            
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

  def close_tab(self, widget, child):
    pagenum = self.page_num(child)
    
    self.remove_page(pagenum)
    #child.destroy()
    del self.already_save[pagenum]
    print pagenum 
