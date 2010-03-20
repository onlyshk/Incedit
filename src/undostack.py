#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# undostack.py - undo/redo provide
# Copyright (C) Kuleshov Alexander 2010 <kuleshovmail@gmail.com>
# 
# Incedit is free software: you can redistribute it and/or modify it
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
import sys, os.path, pango
import locale
import cairo
import gtk.gdk
import re
import gobject

class Feature(object):

    def __init__(self, buffer):
        assert buffer is not None
        self.buffer = buffer


    def _print_range(self, start, end):
        print "RANGE:", repr(self.buffer.get_text(start, end))

    def _print_char(self, iter):
        end = iter.copy()
        end.forward_char()
        print "CHAR:", repr(self.buffer.get_text(iter, end))

bullet_point_re = re.compile(r'^(?:\d+\.|[\*\-])$')

class ListIndent(Feature):
    def __init__(self, buffer):
        Feature.__init__(self, buffer)
        self.bullet_point = u'.'
        self.lock_signals = None
        self.start_tag = buffer.create_tag('list-start',
                                           left_margin = 30,
                                           pixels_above_lines = 12)
        self.bullet_tag = buffer.create_tag('list-bullet',
                                            left_margin = 30)
        self.list_tag   = buffer.create_tag('list',
                                            left_margin        = 30,
                                            pixels_above_lines = 3)
        buffer.connect_after('insert-text',  self._on_buffer_insert_text_after)
        buffer.connect('delete-range',   self._on_buffer_delete_range)
        buffer.connect('mark-set',       self._on_buffer_mark_set)


    def _on_buffer_mark_set(self, buffer, iter, mark):
        if mark.get_name() != 'insert':
            return
        if not iter.has_tag(self.bullet_tag):
            return
        if self.lock_signals:
            return
        self.lock_signals = True
        next = iter.copy()
        next.forward_char()
        if next.has_tag(self.bullet_tag):
            iter.forward_to_tag_toggle(self.bullet_tag)
        else:
            iter.backward_to_tag_toggle(self.bullet_tag)
            iter.backward_char()
        buffer.place_cursor(iter)
        self.lock_signals = False

    def _to_list_start(self, iter):
        self._to_list_item_start(iter)
        while not iter.is_start():
            next = iter.copy()
            next.backward_line()
            if not self._at_bullet_point(next):
                break
            iter = next

    def _to_list_end(self, iter):
        while True:
            self._to_list_item_end(iter)
            iter.forward_char()
            if iter.is_end():
                return
            if not self._at_bullet_point(iter):
                iter.backward_char()
                return

    def _to_list_item_start(self, iter):
        iter.set_line(iter.get_line())

    def _to_list_item_end(self, iter):
        iter.forward_line()
        if iter.is_end():
            return
        iter.backward_char()

    def _at_bullet_point(self, iter):
        end = iter.copy()
        end.forward_find_char(lambda x, d: x == ' ')
        if end.is_end() or end.get_line() != iter.get_line():
            return False
        text = self.buffer.get_text(iter, end)
        if text == self.bullet_point or bullet_point_re.match(text):
            return True
        return False

    def _insert_inside_list(self, buffer, start, end):
        insert_start = buffer.get_iter_at_offset(start)
        insert_end   = buffer.get_iter_at_offset(end)
        text         = buffer.get_text(insert_start, insert_end)
        item_start   = insert_start.copy()
        self._to_list_item_start(item_start)
        list_end     = insert_end.copy()
        self._to_list_end(list_end)
        bullet_end   = item_start.copy()
        bullet_end.forward_to_tag_toggle(self.bullet_tag)
        bullet_point = buffer.get_text(item_start, bullet_end)

        buffer.apply_tag(self.list_tag, item_start, list_end)
        if text in ('\r', '\n'):
            next_char = list_end.copy()
            next_char.forward_char()
            buffer.remove_tag(self.list_tag, list_end, next_char)
            buffer.insert_with_tags(insert_end,
                                    bullet_point,
                                    self.bullet_tag, self.list_tag)


    def _insert_outside_list(self, buffer, insert_start_off, insert_end_off):
        iter = buffer.get_iter_at_offset(insert_start_off)
        iter.set_line(iter.get_line())

        if not self._at_bullet_point(iter):
            return

        while iter.get_offset() < insert_end_off:
            if not self._at_bullet_point(iter):
                iter.forward_line()
                continue
            start_off = iter.get_offset()
            start     = iter.copy()
            next_char = iter.copy()
            next_char.forward_find_char(lambda x, d: x == ' ')
            buffer.delete(start, next_char)
            buffer.insert(start, self.bullet_point)
            start   = buffer.get_iter_at_offset(start_off)
            end_off = start_off + len(self.bullet_point) + 1
            end     = buffer.get_iter_at_offset(end_off)
            buffer.apply_tag(self.bullet_tag, start, end)
            iter = buffer.get_iter_at_offset(start_off)
            iter.forward_line()

        start = buffer.get_iter_at_offset(insert_start_off)
        self._to_list_start(start)
        end   = start.copy()
        end.forward_to_tag_toggle(self.bullet_tag)
        buffer.apply_tag(self.start_tag,  start, end)
        buffer.apply_tag(self.bullet_tag, start, end)

        self._to_list_end(end)
        buffer.apply_tag(self.list_tag, start, end)

    def _on_buffer_insert_text_after(self, buffer, iter, text, length):
        if self.lock_signals:
            return
        self.lock_signals = True
        end      = iter.get_offset()
        start    = end - len(unicode(text))
        previous = buffer.get_iter_at_offset(start - 1)
        if previous.has_tag(self.list_tag):
            self._insert_inside_list(buffer, start, end)
        else:
            self._insert_outside_list(buffer, start, end)
        self.lock_signals = False

    def _delete_inside_list(self, start, end):
        if not start.has_tag(self.list_tag) and not self._at_bullet_point(end):
            next_item_start = end.copy()
            self._to_list_item_end(next_item_start)
            next_item_start.forward_line()
            self.buffer.remove_tag(self.list_tag, end, next_item_start)

            if self._at_bullet_point(next_item_start):
                bullet_end = next_item_start.copy()
                bullet_end.forward_to_tag_toggle(self.bullet_tag)
                self.buffer.apply_tag(self.start_tag,
                                      next_item_start,
                                      bullet_end)
            return

        if start.has_tag(self.start_tag):
            start.backward_to_tag_toggle(self.start_tag)
            item_end = end.copy()
            self._to_list_item_end(item_end)
            item_end.forward_char()
            self.buffer.remove_tag(self.list_tag, start, item_end)
            if not item_end.has_tag(self.bullet_tag):
                return
            bullet_end = item_end.copy()
            bullet_end.forward_to_tag_toggle(self.bullet_tag)
            self.buffer.apply_tag(self.start_tag, item_end, bullet_end)
            return

        if start.has_tag(self.bullet_tag):
            start.backward_to_tag_toggle(self.bullet_tag)
            prev_char = start.copy()
            prev_char.backward_char()
            
            next_item = end.copy()
            self._to_list_item_end(next_item)
            next_item.forward_char()
            self.buffer.remove_tag(self.list_tag, prev_char, next_item)

            if next_item.has_tag(self.bullet_tag):
                bullet_end = next_item.copy()
                bullet_end.forward_to_tag_toggle(self.bullet_tag)
                self.buffer.apply_tag(self.start_tag, next_item, bullet_end)

        if end.has_tag(self.bullet_tag):
            end.forward_to_tag_toggle(self.bullet_tag)

        end_line = end.copy()
        self._to_list_item_start(end_line)
        if end_line.has_tag(self.bullet_tag):
            return
        next = end.copy()
        self._to_list_item_end(next)
        if not next.is_end():
            next.backward_char()
        self.buffer.apply_tag(self.list_tag, end, next)

    def _delete_outside_list(self, start, end):
        next = start.copy()
        next.forward_char()
        text = self.buffer.get_text(start, next)
        if text not in ('\r', '\n'):
            return
        previous = start.copy()
        previous.backward_char()
        if not previous.has_tag(self.list_tag):
            return
        item_end = end.copy()
        self._to_list_item_end(item_end)
        self.buffer.apply_tag(self.list_tag, end, item_end)

    def _on_buffer_delete_range(self, buffer, start, end):
        if self.lock_signals:
            return
        self.lock_signals = True
        if start.has_tag(self.list_tag) or end.has_tag(self.list_tag):
            self._delete_inside_list(start, end)
        else:
            self._delete_outside_list(start, end)
        self.lock_signals = False

class LayoutBox(object):
    annotation = None
    pull       = 0
    y          = 0
    height     = 0

    def __init__(self, parent, annotation):
        self.parent     = parent
        self.annotation = annotation
        self.annotation.connect('size-allocate', self._on_annotation_allocate)

    def _on_annotation_allocate(self, annotation, rect):
        self.height = rect.height
        self.parent.widget._update_annotations()
        
class Layout(object):
    def __init__(self, widget, *args, **kwargs):
        self.widget      = widget
        self.annotations = []
        self.boxes       = {}
        self.padding     = kwargs.get('padding', 0)

    def add(self, annotation):
        self.annotations.append(annotation)
        self.boxes[annotation] = LayoutBox(self, annotation)

    def remove(self, annotation):
        self.annotations.remove(annotation)
        del self.boxes[annotation]

    def pull(self, annotation, position):
        self.boxes[annotation].pull = position

    def sort(self, sort_func):
        self.annotations.sort(sort_func)

    def get_children(self):
        return self.annotations

    def get_annotation_position(self, annotation):
        box = self.boxes[annotation]
        return self.padding, box.y

    def _try_move_up(self, number, delta):
        if delta == 0:
            return
        annotation = self.annotations[number]
        box        = self.boxes[annotation]
        if number == 0:
            box.y = max(0, box.y - delta)
            return
        previous_annotation = self.annotations[number - 1]
        previous_box        = self.boxes[previous_annotation]
        previous_box_end    = previous_box.y + previous_box.height
        possible_delta      = max(0, box.y - previous_box_end)
        if possible_delta >= delta:
            box.y -= delta
            return
        box.y -= possible_delta
        if possible_delta != delta:
            self._try_move_up(number - 1, (delta - possible_delta) / 2)
            box.y = previous_box.y + previous_box.height

    def _dbg(self, action, number):
        return
        annotation = self.annotations[number]
        box        = self.boxes[annotation]
        values     = action, number, box.height, box.pull, box.y
        print "%s: Box %d (h%d) with pull %d is at %d" % values

    def update(self, width, height):
        for n, annotation in enumerate(self.annotations):
            box   = self.boxes[annotation]
            box.y = max(0, box.pull - box.height / 2)
            self._dbg('default', n)

            if n == 0:
                continue

            previous_annotation = self.annotations[n - 1]
            previous_box        = self.boxes[previous_annotation]
            previous_box_end    = previous_box.y + previous_box.height
            if previous_box_end >= box.y:
                self._dbg('moving', n - 1)
                self._try_move_up(n - 1, (previous_box_end - box.y) / 2)
                self._dbg('moved', n - 1)
                box.y = previous_box.y + previous_box.height
                self._dbg('moved', n)

        for n, annotation in enumerate(self.annotations):
            box = self.boxes[annotation]
            self._dbg('showing', n)
            self.widget.move_child(annotation, self.padding, box.y)

class Undoable(object):
    def __init__(self, buffer, startiter = None):
        self.buffer = buffer
        self.start  = None
        if startiter is not None:
            self.start = startiter.get_offset()

    def undo(self):
        raise Exception("Not implemented")

    def redo(self):
        raise Exception("Not implemented")
        
class UndoApplyTag(Undoable):
    def __init__(self, buffer, startiter, enditer, tag):
        Undoable.__init__(self, buffer, startiter)
        self.end      = enditer.get_offset()
        self.old_tags = buffer.get_tags_at_offset(self.start, self.end)
        self.tag      = tag

    def undo(self):
        self.buffer.remove_tag_at_offset(self.tag, self.start, self.end)
        self.buffer.apply_tags_at_offset(self.old_tags, self.start, self.end)

    def redo(self):
        self.buffer.apply_tag_at_offset(self.tag, self.start, self.end)
        
class UndoCollection(Undoable):
    def __init__(self, buffer):
        Undoable.__init__(self, buffer, None)
        self.children = []

    def add(self, child):
        self.children.append(child)

    def undo(self):
        for child in reversed(self.children):
            child.undo()

    def redo(self):
        for child in self.children:
            child.redo()

class UndoDeleteText(Undoable):
    def __init__(self, buffer, startiter, enditer):
        Undoable.__init__(self, buffer, startiter)
        self.end  = enditer.get_offset()
        self.tags = buffer.get_tags_at_offset(self.start, self.end)
        self.text = buffer.get_text(startiter, enditer)

    def undo(self):
        self.buffer.insert_at_offset(self.start, self.text)
        self.buffer.apply_tags_at_offset(self.tags, self.start, self.end)

    def redo(self):
        self.buffer.delete_range_at_offset(self.start, self.end)

class UndoInsertText(Undoable):
    def __init__(self, buffer, startiter, text):
        Undoable.__init__(self, buffer, startiter)
        self.end  = self.start + len(unicode(text))
        self.text = text

    def undo(self):
        self.buffer.delete_range_at_offset(self.start, self.end)

    def redo(self):
        self.buffer.insert_at_offset(self.start, self.text)
        
class UndoRemoveTag(Undoable):
    def __init__(self, buffer, startiter, enditer, tag):
        Undoable.__init__(self, buffer, startiter)
        self.end      = enditer.get_offset()
        self.old_tags = buffer.get_tags_at_offset(self.start, self.end)
        self.tag      = tag

    def undo(self):
        self.buffer.apply_tags_at_offset(self.old_tags, self.start, self.end)

    def redo(self):
        self.buffer.remove_tag_at_offset(self.tag, self.start, self.end)

class TextBuffer(gtk.TextBuffer):
    def __init__(self, *args, **kwargs):
        gtk.TextBuffer.__init__(self, *args)
        self.undo_stack      = []
        self.redo_stack      = []
        self.current_undo    = UndoCollection(self)
        self.lock_undo       = False
        self.max_undo        = 250
        self.max_redo        = 250
        self.undo_freq       = 300
        self.undo_timeout_id = None
        self.user_action     = 0
        self.active_features = []
        self.connect('insert-text',       self._on_insert_text)
        self.connect('delete-range',      self._on_delete_range)
        self.connect('apply-tag',         self._on_apply_tag)
        self.connect('remove-tag',        self._on_remove_tag)
        self.connect('begin-user-action', self._on_begin_user_action)
        self.connect('end-user-action',   self._on_end_user_action)

        features = (
            ('list-indent', True, ListIndent, ()),
        )
        for name, default, feature, feature_args in features:
            active = kwargs.get(name, default)
            if active:
                self.activate_feature(feature, *feature_args)
        self._update_timestamp()

    def activate_feature(self, feature, *args):
        self.active_features.append(feature(self, *args))

    def _cancel_undo_timeout(self):
        if self.undo_timeout_id is None:
            return
        gobject.source_remove(self.undo_timeout_id)
        self.undo_timeout_id = None
        self.end_user_action()

    def _update_timestamp(self):
        if self.undo_timeout_id is not None:
            gobject.source_remove(self.undo_timeout_id)
        else:
            self.begin_user_action()
        self.undo_timeout_id = gobject.timeout_add(self.undo_freq,
                                                   self._cancel_undo_timeout)

    def _on_insert_text(self, buffer, start, text, length):
        if self.lock_undo:
            return
        self._update_timestamp()
        item = UndoInsertText(self, start, text)
        self.current_undo.add(item)
        self.emit('undo-stack-changed')

    def _on_delete_range(self, buffer, start, end):
        if self.lock_undo:
            return
        self._update_timestamp()
        item = UndoDeleteText(self, start, end)
        self.current_undo.add(item)

    def _on_apply_tag(self, buffer, tag, start, end):
        if self.lock_undo:
            return
        self._update_timestamp()
        item = UndoApplyTag(self, start, end, tag)
        self.current_undo.add(item)

    def _on_remove_tag(self, buffer, tag, start, end):
        if self.lock_undo:
            return
        self._update_timestamp()
        item = UndoRemoveTag(self, start, end, tag)
        self.current_undo.add(item)

    def _on_begin_user_action(self, buffer):
        self.user_action += 1

    def _on_end_user_action(self, buffer):
        self.user_action -= 1
        if self.user_action != 0:
            return
        if self.current_undo is None:
            return
        if len(self.current_undo.children) == 0:
            return
        self._undo_add(self.current_undo)
        self.redo_stack = []
        self.current_undo = UndoCollection(self)

    def _undo_add(self, item):
        self.undo_stack.append(item)
        while len(self.undo_stack) >= self.max_undo:
            self.undo_stack.pop(0)
        self.emit('undo-stack-changed')

    def _redo_add(self, item):
        self.redo_stack.append(item)
        while len(self.redo_stack) >= self.max_redo:
            self.redo_stack.pop(0)
        self.emit('undo-stack-changed')

    def insert_at_offset(self, offset, text):
        iter = self.get_iter_at_offset(offset)
        self.insert(iter, text)

    def delete_range_at_offset(self, start, end):
        start = self.get_iter_at_offset(start)
        end   = self.get_iter_at_offset(end)
        self.delete(start, end)

    def apply_tag_at_offset(self, tag, start, end):
        start = self.get_iter_at_offset(start)
        end   = self.get_iter_at_offset(end)
        self.apply_tag(tag, start, end)

    def remove_tag_at_offset(self, tag, start, end):
        start = self.get_iter_at_offset(start)
        end   = self.get_iter_at_offset(end)
        self.remove_tag(tag, start, end)

    def get_tags_at_offset(self, start, end):
        taglist = []
        iter    = self.get_iter_at_offset(start)
        while True:
            taglist.append(iter.get_tags())
            iter.forward_char()
            if iter.get_offset() >= end:
                break
        return taglist

    def apply_tags_at_offset(self, taglist, start, end):
        end   = self.get_iter_at_offset(start + 1)
        start = self.get_iter_at_offset(start)
        for tags in taglist:
            for tag in tags:
                self.apply_tag(tag, start, end)
            start.forward_char()
            end.forward_char()

    def can_undo(self):
        if self.current_undo is not None \
          and len(self.current_undo.children) > 0:
            return True
        return len(self.undo_stack) > 0

    def undo(self):
        self._cancel_undo_timeout()
        if len(self.undo_stack) == 0:
            return
        self.lock_undo = True
        item = self.undo_stack.pop()
        item.undo()
        self._redo_add(item)
        self.lock_undo = False

    def can_redo(self):
        return len(self.redo_stack) > 0

    def redo(self):
        self._cancel_undo_timeout()
        if len(self.redo_stack) == 0:
            return
        self.lock_undo = True
        item = self.redo_stack.pop()
        item.redo()
        self._undo_add(item)
        self.lock_undo = False

gobject.signal_new('undo-stack-changed',
                   TextBuffer,
                   gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE,
                   ())

gobject.type_register(TextBuffer)

class TextEditor(gtk.TextView):
    def __init__(self, textbuffer = None, *args, **kwargs):
        if textbuffer is None:
            textbuffer = TextBuffer()
        gtk.TextView.__init__(self, textbuffer, *args, **kwargs)
        self.anno_width       = 200
        self.anno_padding     = 10
        self.anno_layout      = Layout(self)
        self.annotations      = {}
        self.show_annotations = True
        self.set_right_margin(50 + self.anno_padding)
        self.connect('expose_event', self._on_expose_event)
        self.get_buffer().connect('mark-set', self._on_buffer_mark_set)
        self.set_wrap_mode(gtk.WRAP_WORD)


    def _on_buffer_mark_set(self, buffer, iter, mark):
        self._update_annotations()


    def _on_expose_event(self, widget, event):
        text_window = widget.get_window(gtk.TEXT_WINDOW_TEXT)
        if event.window != text_window:
            return

        # Create the cairo context.
        ctx = event.window.cairo_create()

        # Restrict Cairo to the exposed area; avoid extra work
        ctx.rectangle(event.area.x,
                      event.area.y,
                      event.area.width,
                      event.area.height)
        ctx.clip()

        self.draw(ctx, *event.window.get_size())

    def draw(self, ctx, w, h):
        if ctx is None:
            return
        if not self.show_annotations:
            return

        ctx.set_line_width(1)
        ctx.set_dash((3, 2))
        right_margin = self.get_right_margin()
        for annotation in self.anno_layout.get_children():
            mark_x, mark_y = self._get_annotation_mark_position(annotation)
            anno_x, anno_y = self.anno_layout.get_annotation_position(annotation)
            anno_x, anno_y, anno_w, anno_h = annotation.get_allocation()
            path = [(mark_x,           mark_y - 5),
                    (mark_x,           mark_y),
                    (w - right_margin, mark_y),
                    (w,                anno_y + anno_h / 2)]

            stroke_color = annotation.get_border_color()
            ctx.set_source_rgba(*color.to_rgba(stroke_color))
            ctx.move_to(*path[0])
            for x, y in path[1:]:
                ctx.line_to(x, y)
            ctx.stroke()

    def _get_annotation_mark_offset(self, annotation1, annotation2):
        iter1 = self.get_buffer().get_iter_at_mark(annotation1.mark)
        iter2 = self.get_buffer().get_iter_at_mark(annotation2.mark)
        off1  = iter1.get_line()
        off2  = iter2.get_line()
        if off1 == off2:
            return iter2.get_offset() - iter1.get_offset()
        return off1 - off2

    def _get_annotation_mark_position(self, annotation):
        iter           = self.get_buffer().get_iter_at_mark(annotation.mark)
        rect           = self.get_iter_location(iter)
        mark_x, mark_y = rect.x, rect.y + rect.height
        return self.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT,
                                            mark_x,
                                            mark_y)

    def _update_annotation(self, annotation):
        item_width = self.anno_width - 2 * self.anno_padding
        annotation.set_size_request(item_width, -1)
        mark_x, mark_y = self._get_annotation_mark_position(annotation)
        self.anno_layout.pull(annotation, mark_y)

    def _update_annotation_area(self):
        self.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, self.anno_width)
        bg_color = self.get_style().base[gtk.STATE_NORMAL]
        window   = self.get_window(gtk.TEXT_WINDOW_RIGHT)
        window.set_background(bg_color)


    def _update_annotations(self):
        if not self.show_annotations:
            return
        iter   = self.get_buffer().get_end_iter()
        rect   = self.get_iter_location(iter)
        height = rect.y + rect.height
        self.anno_layout.sort(self._get_annotation_mark_offset)
        for annotation in self.anno_layout.get_children():
            self._update_annotation(annotation)
        self.anno_layout.update(self.anno_width, height)
        self.queue_draw()

    def set_annotation_area_width(self, width, padding = 10):
        self.anno_width   = width
        self.anno_padding = padding
        self._update_annotations()

    def add_annotation(self, annotation):
        self.annotations[annotation.mark] = annotation
        if self.show_annotations == False:
            return
        self._update_annotation_area()
        self.anno_layout.add(annotation)
        self.add_child_in_window(annotation,
                                 gtk.TEXT_WINDOW_RIGHT,
                                 self.anno_padding,
                                 0)
        self._update_annotations()

    def remove_annotation(self, annotation):
        self.anno_layout.remove(annotation)
        del self.annotations[annotation.mark]
        self.remove(annotation)

    def set_show_annotations(self, active = True):
        if self.show_annotations == active:
            return

        self.show_annotations = active
        if active:
            for annotation in self.annotations.itervalues():
                self.add_annotation(annotation)
        else:
            for annotation in self.annotations.itervalues():
                self.anno_layout.remove(annotation)
                self.remove(annotation)
            self.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, 0)
