#!/usr/bin/env python3

'''
    Copyright 2018 Adi Hezral (hezral@gmail.com)
    This file is part of Clips ("Application").
    The Application is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    The Application is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this Application.  If not, see <http://www.gnu.org/licenses/>.
'''

from Xlib.protocol import event
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Granite, Gdk, Pango, Gio, GObject, GLib


class CustomDialog(Gtk.Window):
    def __init__(self, dialog_parent_widget, dialog_title, dialog_content_widget, action_button_label, action_button_name, action_callback, action_type, size=None, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parent_window = dialog_parent_widget.get_toplevel()

        def close_dialog(button):
            dialog_content_widget.destroy()
            self.destroy()

        def on_key_press(self, eventkey):
            if eventkey.keyval == 65307: #63307 is esc key
                dialog_content_widget.destroy()
                self.destroy()

        self.header = Gtk.HeaderBar()
        self.header.props.show_close_button = False
        self.header.props.title = dialog_title
        self.header.get_style_context().add_class("default-decoration")
        self.header.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)

        grid = Gtk.Grid()
        grid.props.expand = True
        grid.props.margin_top = 0
        grid.props.margin_bottom = grid.props.margin_left = grid.props.margin_right = 15
        grid.props.row_spacing = 10
        grid.props.column_spacing = 10
        grid.attach(dialog_content_widget, 0, 0, 2, 1)

        if action_type is not None:
            dialog_parent_widget.ok_button = Gtk.Button(label=action_button_label)
            dialog_parent_widget.ok_button.props.name = action_button_name
            dialog_parent_widget.ok_button.props.expand = False
            dialog_parent_widget.ok_button.props.halign = Gtk.Align.END
            dialog_parent_widget.ok_button.set_size_request(65,25)
            if action_type == "destructive":
                dialog_parent_widget.ok_button.get_style_context().add_class("destructive-action")
            else:
                dialog_parent_widget.ok_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

            dialog_parent_widget.cancel_button = Gtk.Button(label="Cancel")
            dialog_parent_widget.cancel_button.props.hexpand = True
            dialog_parent_widget.cancel_button.props.halign = Gtk.Align.END
            dialog_parent_widget.cancel_button.set_size_request(65,25)

            dialog_parent_widget.ok_button.connect("clicked", action_callback, (data, dialog_parent_widget.cancel_button))
            dialog_parent_widget.cancel_button.connect("clicked", close_dialog)

            grid.attach(dialog_parent_widget.cancel_button, 0, 1, 1, 1)
            grid.attach(dialog_parent_widget.ok_button, 1, 1, 1, 1)

        if size is not None:
            self.set_size_request(size[0],size[1])
        else:
            self.set_size_request(150,100)

        self.get_style_context().add_class("rounded")
        self.set_titlebar(self.header)
        self.props.transient_for = parent_window
        self.props.modal = True
        self.props.resizable = False
        self.props.window_position = Gtk.WindowPosition.CENTER_ON_PARENT
        self.add(grid)
        self.show_all()
        self.connect("destroy", close_dialog)
        self.connect("key-press-event", on_key_press)


class SettingsGroup(Gtk.Grid):

    CSS = '''
    frame#settings-group-frame {
        border-radius: 4px;
        border-color: rgba(0, 0, 0, 0.3);
        background-color: @shaded_dark;
    }

    .settings-sub-label {
        font-size: 0.9em;
        color: gray;
    }
    '''

    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(CSS.encode())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def __init__(self, group_label=None, subsettings_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        grid = Gtk.Grid()
        grid.props.margin = 8
        grid.props.hexpand = True
        grid.props.row_spacing = 8
        grid.props.column_spacing = 10

        i = 0
        for subsetting in subsettings_list:
            grid.attach(subsetting, 0, i, 1, 1)
            i += 1

        frame = Gtk.Frame()
        frame.props.name = "settings-group-frame"
        frame.props.hexpand = True
        frame.add(grid)
        self.attach(frame, 0, 1, 1, 1)

        if group_label is not None:
            label = Gtk.Label(group_label)
            label.props.name = "settings-group-label"
            label.props.halign = Gtk.Align.START
            label.props.margin_left = 4
            self.attach(label, 0, 0, 1, 1)

        self.props.name = "settings-group"
        self.props.halign = Gtk.Align.FILL
        self.props.hexpand = True
        self.props.row_spacing = 4
        self.props.can_focus = False


class SubSettings(Gtk.Grid):
    def __init__(self, type=None, name=None, label=None, sublabel=None, separator=True, params=None, utils=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.type = type

        # box---
        box = Gtk.VBox()
        box.props.spacing = 2
        box.props.hexpand = True

        # label---
        if label is not None:
            self.label_text = Gtk.Label(label)
            self.label_text.props.halign = Gtk.Align.START
            box.add(self.label_text)
        
        # sublabel---
        if sublabel is not None:
            self.sublabel_text = Gtk.Label(sublabel)
            self.sublabel_text.props.halign = Gtk.Align.START
            self.sublabel_text.props.wrap_mode = Pango.WrapMode.WORD
            self.sublabel_text.props.max_width_chars = 30
            self.sublabel_text.props.justify = Gtk.Justification.LEFT
            #self.sublabel_text.props.wrap = True
            self.sublabel_text.get_style_context().add_class("settings-sub-label")
            box.add(self.sublabel_text)

        if type == "switch":
            self.switch = Gtk.Switch()
            self.switch.props.name = name
            self.switch.props.halign = Gtk.Align.END
            self.switch.props.valign = Gtk.Align.CENTER
            self.switch.props.hexpand = False
            self.attach(self.switch, 1, 0, 1, 2)

        if type == "spinbutton":
            self.spinbutton = Gtk.SpinButton().new_with_range(min=params[0], max=params[1], step=params[2])
            self.spinbutton.props.name = name
            self.attach(self.spinbutton, 1, 0, 1, 2)

        if type == "button":
            if len(params) == 1:
                self.button = Gtk.Button(label=params[0])
            else:
                self.button = Gtk.Button(label=params[0], image=params[1])
            self.button.props.name = name
            self.button.props.hexpand = False
            self.button.props.always_show_image = True
            self.button.set_size_request(90, -1)
            if len(params) >1:
                label = [child for child in self.button.get_children()[0].get_child() if isinstance(child, Gtk.Label)][0]
                label.props.valign = Gtk.Align.CENTER
            self.attach(self.button, 1, 0, 1, 2)

        if type == "checkbutton":
            self.checkbutton = Gtk.CheckButton().new_with_label(params[0])
            self.checkbutton.props.name = name
            self.attach(self.checkbutton, 0, 0, 1, 2)

        # separator ---
        if separator:
            row_separator = Gtk.Separator()
            row_separator.props.hexpand = True
            row_separator.props.valign = Gtk.Align.CENTER
            if type == None:
                self.attach(row_separator, 0, 0, 1, 1)
            else:
                self.attach(row_separator, 0, 2, 2, 1)
        
        # SubSettings construct---
        self.props.name = name
        self.props.hexpand = True
        if type == None:
            self.attach(box, 0, 0, 1, 1)
        else:
            self.props.row_spacing = 8
            self.props.column_spacing = 10
            self.attach(box, 0, 0, 1, 2)


class Settings(Gtk.Grid):
    def __init__(self, gtk_application, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = gtk_application

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.props.row_spacing = 10

        # display -------------------------------------------------
        theme_switch = SubSettings(type="switch", name="theme-switch", label="Switch between Dark/Light theme", sublabel=None, separator=False)
        theme_optin = SubSettings(type="checkbutton", name="theme-optin", label=None, sublabel=None, separator=True, params=("Follow system appearance style",))

        theme_switch.switch.bind_property("active", self.app.gtk_settings, "gtk-application-prefer-dark-theme", GObject.BindingFlags.SYNC_CREATE)

        self.app.granite_settings.connect("notify::prefers-color-scheme", self.on_appearance_style_change, theme_switch)
        theme_switch.switch.connect_after("notify::active", self.on_switch_activated)
        theme_optin.checkbutton.connect_after("notify::active", self.on_checkbutton_activated, theme_switch)
        
        self.app.gio_settings.bind("prefer-dark-style", theme_switch.switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.app.gio_settings.bind("theme-optin", theme_optin.checkbutton, "active", Gio.SettingsBindFlags.DEFAULT)

        # persistent_mode = SubSettings(type="switch", name="persistent-mode", label="Persistent mode", sublabel="Stays open and updates as new clips added",separator=True)
        # persistent_mode.switch.connect_after("notify::active", self.on_switch_activated)
        # self.app.gio_settings.bind("persistent-mode", persistent_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)
        
        sticky_mode = SubSettings(type="switch", name="sticky-mode", label="Sticky mode", sublabel="Display on all workspaces",separator=False)
        sticky_mode.switch.connect_after("notify::active", self.on_switch_activated)
        self.app.gio_settings.bind("sticky-mode", sticky_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        always_on_top = SubSettings(type="switch", name="always-on-top", label="Always on top", sublabel="Display above all windows",separator=True)
        always_on_top.switch.connect_after("notify::active", self.on_switch_activated)
        self.app.gio_settings.bind("always-on-top", always_on_top.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        display_behaviour_settings = SettingsGroup("Display", (theme_switch, theme_optin, always_on_top, sticky_mode, ))
        self.add(display_behaviour_settings)

        # Behaviour -------------------------------------------------
        shake_reveal = SubSettings(type="switch", name="shake-reveal", label="Shake to reveal", sublabel="Shake mouse to reveal app",separator=True)
        shake_reveal.switch.connect_after("notify::active", self.on_switch_activated)
        self.app.gio_settings.bind("shake-reveal", shake_reveal.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        shake_sensitivity = SubSettings(type="spinbutton", name="shake-sensitivity", label="Shake sensitivity", sublabel="Adjust shake to reveal sensitivity", separator=False, params=(3,10,1))
        shake_sensitivity.spinbutton.connect("value-changed", self.on_spinbutton_activated)
        self.app.gio_settings.bind("shake-sensitivity", shake_sensitivity.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        app_settings = SettingsGroup("Behaviour (restart required)", (shake_reveal, shake_sensitivity, ))
        self.add(app_settings)
    

    def on_checkbutton_activated(self, checkbutton, gparam, widget):
        name = checkbutton.get_name()
        theme_switch = widget
        if name == "theme-optin":
            if self.app.gio_settings.get_value("theme-optin"):
                prefers_color_scheme = self.app.granite_settings.get_prefers_color_scheme()
                sensitive = False
            else:
                prefers_color_scheme = Granite.SettingsColorScheme.NO_PREFERENCE
                theme_switch.switch.props.active = self.app.gio_settings.get_value("prefer-dark-style")
                sensitive = True

            self.app.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)
            self.app.granite_settings.connect("notify::prefers-color-scheme", self.app.on_prefers_color_scheme)

            if "DARK" in prefers_color_scheme.value_name:
                active = True
            else:
                active = False

            theme_switch.switch.props.active = active
            theme_switch.props.sensitive = sensitive

    def on_appearance_style_change(self, granite_settings, gparam, widget):
        theme_switch = widget
        if theme_switch.switch.props.active:
            theme_switch.switch.props.active = False
        else:
            theme_switch.switch.props.active = True

    def on_spinbutton_activated(self, spinbutton):        
        name = spinbutton.get_name()
        main_window = self.app.main_window

        # if self.is_visible():
            # if name == "shake-sensitivity":
                # GLib.idle_add(main_window.setup_mouse_listener, None)

    def on_switch_activated(self, switch, gparam):
        name = switch.get_name()
        main_window = self.app.main_window
        
        if self.is_visible():

            if name == "persistent-mode":
                if switch.get_active():
                    # print('state-flags-on')
                    main_window.disconnect_by_func(main_window.on_persistent_mode)
                else:
                    main_window.connect("state-flags-changed", main_window.on_persistent_mode)
                    # print('state-flags-off')

            if name == "sticky-mode":
                if switch.get_active():
                    main_window.stick()
                else:
                    main_window.unstick()

            if name == "always-on-top":
                if switch.get_active():
                    main_window.set_keep_above(True)
                else:
                    main_window.set_keep_above(False)

            # if name == "shake-reveal":
            #     # main_window.setup_shake_listener()
            #     if switch.get_active():
            #         print("enable-shake")
            #         main_window.setup_shake_listener()
            #         print(main_window.shake_listener.listener)
            #         print(main_window.shake_listener.running)
            #     else:
            #         print("disable-shake")
            #         main_window.shake_listener.remove_listener()
            #         print(main_window.shake_listener.listener)
            #         print(main_window.shake_listener.running)