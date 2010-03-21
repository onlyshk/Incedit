#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# about.py - About form
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
import tab
 
def on_clicked(widget):
     about = gtk.AboutDialog()
     about.set_program_name("Incedit")
     about.set_version("0.1.3")
     about.set_copyright("(c) Kuleshov Alexander <kuleshovmail@gmail.com>")
     about.set_comments("Incedit - it's lightweight editor")
     about.set_website("http://github.com/onlyshk/Incedit")
     about.run()
     about.destroy()
 
