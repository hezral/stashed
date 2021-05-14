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
        
        self.main_window = None

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
        self.main_window = self.props.active_window
        if not self.main_window:
            self.main_window = StashedWindow(application=self)

        # self.main_window.set_keep_above(True)
        self.main_window.present()
        self.main_window.stash_grid.grab_focus()
        # GLib.timeout_add(100, self.main_window.set_keep_above, False) # need to put time gap else won't work to bring window front

        self.create_app_actions()

    def on_prefers_color_scheme(self, *args):
        prefers_color_scheme = self.granite_settings.get_prefers_color_scheme()
        self.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)

    def create_action(self, name, callback, shortcutkey):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        self.set_accels_for_action("app.{name}".format(name=name), [shortcutkey])

    def on_hide_action(self, action, param):
        if self.main_window is not None:
            self.main_window.hide()

    def on_quit_action(self, action, param):
        if self.main_window is not None:
            self.main_window.destroy()

    def create_app_actions(self):
        # app actions
        self.create_action("hide", self.on_hide_action, "Escape")
        self.create_action("quit", self.on_quit_action, "<Ctrl>Q")

def main(version):
    app = Application()
    return app.run(sys.argv)
