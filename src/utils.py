#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# utils.py - simple utils for app
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

#
# cut file only name
#
import incedit 

def cut_file_name(path):

    list_of_split = path.split("/")

    rev_list_of_split = list_of_split[::-1]
 
    file_name = rev_list_of_split[0]
    
    return file_name
