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

gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Gdk, Gio, Granite, GLib

from .window import StashedWindow
from .utils import HelperUtils
from .shake_listener import ShakeListener

class Application(Gtk.Application):

    app_id = "com.github.hezral.stashed"
    granite_settings = Granite.Settings.get_default()
    gtk_settings = Gtk.Settings.get_default()
    gio_settings = Gio.Settings(schema_id=app_id)
    utils = HelperUtils()
    running = False
    shake_listener = None

    def __init__(self):
        super().__init__(application_id=self.app_id,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        self.main_window = None

        self.create_app_actions()

        if self.gio_settings.get_value("theme-optin"):
            prefers_color_scheme = self.granite_settings.get_prefers_color_scheme()
            self.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)
            self.granite_settings.connect("notify::prefers-color-scheme", self.on_prefers_color_scheme)

        provider = Gtk.CssProvider()        
        provider.load_from_path(os.path.join(os.path.dirname(__file__), "data", "application.css"))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.icon_theme = Gtk.IconTheme.get_default()
        self.icon_theme.prepend_search_path("/run/host/usr/share/pixmaps")
        self.icon_theme.prepend_search_path("/run/host/usr/share/icons")
        self.icon_theme.prepend_search_path(os.path.join(GLib.get_home_dir(), ".local/share/flatpak/exports/share/icons"))
        self.icon_theme.prepend_search_path(os.path.join(os.path.dirname(__file__), "data", "icons"))

        self.setup_shake_listener()

    def do_activate(self):
        self.main_window = self.props.active_window
        
        if not self.main_window:
            self.main_window = StashedWindow(application=self)

        self.on_show_window()

        self.running = True

    def on_prefers_color_scheme(self, *args):
        prefers_color_scheme = self.granite_settings.get_prefers_color_scheme()
        self.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)

    def create_action(self, name, callback, shortcutkey):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        self.set_accels_for_action("app.{name}".format(name=name), [shortcutkey])

    def on_hide_action(self, action, param):
        if self.get_windows() is not None:
            for window in self.get_windows():
                window.hide

    def on_quit_action(self, action, param):
        if self.main_window is not None:
            self.main_window.destroy()

    def on_show_window(self):
        for window in self.get_windows():
            window.setup_display_settings()
            window.show()
            window.present()
            window.stash_stacked.grab_focus()


    def create_app_actions(self):
        self.create_action("hide", self.on_hide_action, "Escape")
        self.create_action("quit", self.on_quit_action, "<Ctrl>Q")

    def setup_shake_listener(self, *args):
        if self.shake_listener is not None:
            self.shake_listener.listener.stop()
            self.shake_listener = None
        if self.gio_settings.get_value("shake-reveal"):
            self.shake_listener = ShakeListener(app=self, reveal_callback=self.do_activate, sensitivity=self.gio_settings.get_int("shake-sensitivity"))

def main(version):
    app = Application()
    return app.run(sys.argv)
