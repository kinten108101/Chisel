#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
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
from gi.repository import Gtk

from setzer.dialogs.dialog import Dialog

import os.path


class BuildSaveDialog(Dialog):
    ''' This dialog is asking users to save never saved documents before building. '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self, document):
        self.setup(document)
        response = self.view.run()
        if response == Gtk.ResponseType.YES:
            return_value = True
        else:
            return_value = False
        self.close()
        return return_value

    def setup(self, document):
        self.view = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.QUESTION)

        self.view.set_property('text', _('Document »{document}« has no filename.').format(document=document.get_displayname()))
        self.view.format_secondary_markup(_('Please save your document to a file, so the build system knows where to put the .pdf (it will be in the same folder as your document).'))

        self.view.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL, _('_Save document now'), Gtk.ResponseType.YES)
        self.view.set_default_response(Gtk.ResponseType.YES)


