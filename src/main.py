# main.py
#
# Copyright 2021 Adi Hezral
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import gi

gi.require_version('Handy', '1')
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Gdk, Gio, Granite, GLib

from .window import StashedWindow


class Application(Gtk.Application):

    granite_settings = Granite.Settings.get_default()
    gtk_settings = Gtk.Settings.get_default()

    def __init__(self):
        super().__init__(application_id='com.github.hezral.stashed',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        # prefers_color_scheme = self.granite_settings.get_prefers_color_scheme()
        # self.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)
        # self.granite_settings.connect("notify::prefers-color-scheme", self.on_prefers_color_scheme)

        provider = Gtk.CssProvider()        
        provider.load_from_path(os.path.join(os.path.dirname(__file__), "data", "application.css"))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.icon_theme = Gtk.IconTheme.get_default()
        self.icon_theme.prepend_search_path("/run/host/usr/share/pixmaps")
        self.icon_theme.prepend_search_path("/run/host/usr/share/icons")
        self.icon_theme.prepend_search_path(os.path.join(GLib.get_home_dir(), ".local/share/flatpak/exports/share/icons"))
        self.icon_theme.prepend_search_path(os.path.join(os.path.dirname(__file__), "data", "icons"))

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = StashedWindow(application=self)
        win.present()

    # def on_prefers_color_scheme(self, *args):
    #     prefers_color_scheme = self.granite_settings.get_prefers_color_scheme()
    #     self.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)

def main(version):
    app = Application()
    return app.run(sys.argv)
