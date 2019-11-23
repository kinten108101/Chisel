#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk

from app.service_locator import ServiceLocator


class DocumentController(object):
    
    def __init__(self, document, document_view):

        self.document = document
        self.view = document_view

        self.observe_document()
        self.observe_document_view()
        
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.view.scrolled_window.get_hadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.view.source_view.connect('key-press-event', self.on_keypress)
        
    def observe_document(self):
        self.document.get_buffer().connect('changed', self.on_buffer_changed)
        self.document.get_buffer().connect('mark-set', self.on_mark_set)
        self.document.get_buffer().connect('mark-deleted', self.on_mark_deleted)
        
    def observe_document_view(self):
        self.document.build_widget.view.build_button.connect('clicked', self.build_document_request)
        self.document.build_widget.view.stop_button.connect('clicked', self.on_stop_build_button_click)
        self.document.build_widget.view.clean_button.connect('clicked', self.on_clean_button_click)
        self.view.source_view.connect('focus-out-event', self.on_focus_out)
        self.view.source_view.connect('focus-in-event', self.on_focus_in)

    '''
    *** signal handlers: changes in documents
    '''

    def on_adjustment_value_changed(self, adjustment, user_data=None):
        self.document.autocomplete.update_autocomplete_position(False)
        return False

    def on_mark_set(self, buffer, insert, mark, user_data=None):
        self.document.autocomplete.update_autocomplete_position(False)
    
    def on_buffer_changed(self, buffer, user_data=None):
        self.document.autocomplete.update_autocomplete_position(True)
    
    def on_mark_deleted(self, buffer, mark, user_data=None):
        self.document.autocomplete.update_autocomplete_position(False)
    
    def build_document_request(self, button_object=None):
        if self.document.filename == None:
            if ServiceLocator.get_dialog('build_save').run(self.document):
                ServiceLocator.get_dialog('save_document').run(self.document, '.tex')
            else:
                return False
        if self.document.filename != None:
            self.document.build()

    def on_stop_build_button_click(self, button_object=None):
        document = self.document
        if document != None:
            if document.filename != None:
                self.document.stop_building()
    
    def on_clean_button_click(self, button_object=None):
        document = self.document
        if document != None:
            if document.filename != None:
                self.document.cleanup_build_files()

    def on_keypress(self, widget, event, data=None):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.keyval == Gdk.keyval_from_name('Down'):
            if event.state & modifiers == 0:
                return self.document.autocomplete.on_down_press()

        if event.keyval == Gdk.keyval_from_name('Up'):
            if event.state & modifiers == 0:
                return self.document.autocomplete.on_up_press()

        if event.keyval == Gdk.keyval_from_name('Escape'):
            if event.state & modifiers == 0:
                return self.document.autocomplete.on_escape_press()

        if event.keyval == Gdk.keyval_from_name('Return'):
            if event.state & modifiers == 0:
                return self.document.autocomplete.on_return_press()

        if event.keyval == Gdk.keyval_from_name('Tab') or event.keyval == Gdk.keyval_from_name('ISO_Left_Tab'):
            if event.state & modifiers == 0:
                buffer = self.document.get_buffer()
                insert = buffer.get_iter_at_mark(buffer.get_insert())
                insert.forward_chars(1)
                limit_iter = insert.copy()
                limit_iter.forward_line()
                limit_iter.forward_line()
                limit_iter.backward_chars(1)
                result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.place_cursor(result[0])
                    buffer.select_range(result[0], result[1])
                    self.view.source_view.scroll_to_iter(result[1], 0, False, 0, 0)
                    return True
                
                insert.backward_chars(1)
                result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.view.source_view.scroll_to_iter(result[1], 0, False, 0, 0)
                    return True
            elif event.state & modifiers == Gdk.ModifierType.SHIFT_MASK:
                buffer = self.document.get_buffer()
                insert = buffer.get_iter_at_mark(buffer.get_insert())
                limit_iter = insert.copy()
                limit_iter.backward_line()
                result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.view.source_view.scroll_to_iter(result[0], 0, False, 0, 0)
                    return True

                insert.forward_chars(1)
                result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.view.source_view.scroll_to_iter(result[0], 0, False, 0, 0)
                    return True
        return False

    def on_focus_out(self, widget, event, user_data=None):
        self.document.autocomplete.focus_hide()

    def on_focus_in(self, widget, event, user_data=None):
        self.document.autocomplete.focus_show()

