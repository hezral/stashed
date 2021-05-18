# window.py
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

import os
import gi
gi.require_version('Handy', '1')
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Handy, Gdk, Gio, Granite, GLib, GdkPixbuf, Pango

from .utils import *

IMAGE_DND_TARGET = Gtk.TargetEntry.new('image/png', Gtk.TargetFlags.SAME_APP, 0)
UTF8TEXT_DND_TARGET = Gtk.TargetEntry.new('text/plain;charset=utf-8', Gtk.TargetFlags.SAME_APP, 0)
PLAINTEXT_DND_TARGET = Gtk.TargetEntry.new('text/plain', Gtk.TargetFlags.SAME_APP, 0)
URI_DND_TARGET = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags.SAME_APP, 0)
TARGETS = [URI_DND_TARGET, IMAGE_DND_TARGET, UTF8TEXT_DND_TARGET, PLAINTEXT_DND_TARGET]

class StashedWindow(Handy.Window):
    __gtype_name__ = 'StashedWindow'

    iconstack_offset = 0
    search = []
    search_result = 0

    Handy.init()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app = self.props.application

        self.header = self.generate_headerbar()
        self.stash_stacked_grid = self.generate_stash_stacked()
        self.stash_flowbox_grid = self.generate_stash_flowbox()
        self.stashed_settings_grid = self.generate_stashed_settings()

        self.stack = Gtk.Stack()
        self.stack.props.transition_type = Gtk.StackTransitionType.CROSSFADE
        self.stack.props.transition_duration = 250
        self.stack.add_named(self.stash_stacked_grid, "stash-stacked")
        self.stack.add_named(self.stash_flowbox_grid, "stash-flowbox")
        self.stack.add_named(self.stashed_settings_grid, "stashed-settings")

        grid = Gtk.Grid()
        grid.props.expand = True
        grid.attach(self.header, 0, 0, 1, 1)
        grid.attach(self.stack, 0, 1, 1, 1)

        self.add(grid)
        self.props.resizable = False
        self.props.window_position = Gtk.WindowPosition.MOUSE
        self.show_all()
        self.set_keep_above(True)
        self.set_size_request(400, 400)

        self.drag_and_drop_setup()
        self.drag_and_grab_setup(self.stash_stacked)
        self.drag_and_grab_setup(self.stash_flowbox)

        self.connect("key-press-event", self.on_stash_filtered)

    def generate_headerbar(self):
        menu_button = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral-menu-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        menu_button.props.always_show_image = True
        menu_button.props.can_focus = False
        menu_button.props.margin = 2
        menu_button.set_size_request(16, 16)
        menu_button.get_style_context().remove_class("image-button")
        menu_button.get_style_context().add_class("titlebutton")
        menu_button.connect("clicked", self.on_menu_clicked)

        search_button = Gtk.Button(image=Gtk.Image().new_from_icon_name("system-search-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        search_button.props.always_show_image = True
        search_button.props.can_focus = False
        search_button.props.margin = 2
        search_button.props.margin_right = 0
        search_button.set_size_request(16, 16)
        search_button.get_style_context().remove_class("image-button")
        search_button.get_style_context().add_class("titlebutton")
        search_button.connect("clicked", self.on_search_clicked)

        self.search_revealer = Gtk.Revealer()
        self.search_revealer.props.transition_duration = 2000
        self.search_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        self.search_revealer.add(search_button)

        header = Handy.HeaderBar()
        header.props.hexpand = True
        header.props.title = "Stashed"
        header.props.spacing = 0
        header.props.has_subtitle = False
        header.props.show_close_button = True
        header.props.decoration_layout = "close:"
        header.get_style_context().add_class(Granite.STYLE_CLASS_DEFAULT_DECORATION)
        header.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)
        header.pack_end(menu_button)
        header.pack_end(self.search_revealer)

        return header

    def generate_stash_stacked(self):
        self.stash_stacked = Gtk.Overlay()
        self.stash_stacked.props.name = "stack"
        self.stash_stacked.props.expand = True
        self.stash_stacked.props.valign = self.stash_stacked.props.halign = Gtk.Align.FILL

        clear_stash = Gtk.Button(label="Clear")
        clear_stash.props.hexpand = True
        clear_stash.props.margin = 10
        clear_stash.props.halign = Gtk.Align.CENTER
        clear_stash.connect("clicked", self.on_clear_stash)

        self.clear_stash_revealer = Gtk.Revealer()
        self.clear_stash_revealer.props.transition_duration = 2000
        self.clear_stash_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        self.clear_stash_revealer.add(clear_stash)

        stash_stacked_grid = Gtk.Grid()
        stash_stacked_grid.props.can_focus = True
        stash_stacked_grid.props.row_spacing = 2
        stash_stacked_grid.attach(self.stash_stacked, 0, 0, 1, 1)
        stash_stacked_grid.attach(self.clear_stash_revealer, 0, 1, 1, 1)
        stash_stacked_grid.connect("button-press-event", self.on_stash_grid_clicked)

        return stash_stacked_grid

    def generate_stash_flowbox(self):
        self.stash_flowbox = Gtk.FlowBox()
        self.stash_flowbox.props.expand = True
        self.stash_flowbox.props.homogeneous = True
        self.stash_flowbox.props.row_spacing = 20
        self.stash_flowbox.props.column_spacing = 20
        self.stash_flowbox.props.max_children_per_line = 2
        self.stash_flowbox.props.min_children_per_line = 2
        self.stash_flowbox.props.margin = 20
        self.stash_flowbox.props.valign = Gtk.Align.START
        self.stash_flowbox.props.halign = Gtk.Align.FILL
        self.stash_flowbox.props.selection_mode = Gtk.SelectionMode.MULTIPLE
        self.stash_flowbox.connect("child-activated", self.on_stash_items_flowboxchild_activated)
        self.stash_flowbox.connect("button-press-event", self.on_stash_grid_clicked)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.expand = True
        scrolled_window.add(self.stash_flowbox)
        
        self.search_keyword = Gtk.Label()
        self.search_keyword.props.name = "search-keyword"
        self.search_keyword.props.halign = Gtk.Align.FILL
        self.search_keyword.props.valign = Gtk.Align.START
        self.search_keyword_revealer = Gtk.Revealer()
        self.search_keyword_revealer.add(self.search_keyword)

        self.clear_keyword = Gtk.Button(image=Gtk.Image().new_from_icon_name("edit-clear-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        self.clear_keyword.props.halign = Gtk.Align.END
        self.clear_keyword.connect("clicked", self.on_stash_unfiltered)
        self.clear_keyword_revealer = Gtk.Revealer()
        self.clear_keyword_revealer.add(self.clear_keyword)

        stash_flowbox_grid = Gtk.Grid()
        stash_flowbox_grid.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 0, 1, 1)
        stash_flowbox_grid.attach(self.clear_keyword_revealer, 0, 0, 1, 1)
        stash_flowbox_grid.attach(self.search_keyword_revealer, 0, 0, 1, 1)
        stash_flowbox_grid.attach(scrolled_window, 0, 1, 1, 1)

        return stash_flowbox_grid

    def generate_stashed_settings(self):
        stashed_settings_grid = Gtk.FlowBox()
        stashed_settings_grid.props.expand = True
        stashed_settings_grid.props.homogeneous = True
        stashed_settings_grid.props.row_spacing = 20
        stashed_settings_grid.props.column_spacing = 20
        stashed_settings_grid.props.max_children_per_line = 2
        stashed_settings_grid.props.min_children_per_line = 2
        stashed_settings_grid.props.margin = 20
        stashed_settings_grid.props.valign = Gtk.Align.START
        stashed_settings_grid.props.halign = Gtk.Align.FILL

        add_shortcut = Gtk.Button(label="Add Shortcut", image=Gtk.Image().new_from_icon_name("com.github.hezral-shortcuts", Gtk.IconSize.DIALOG))
        add_shortcut.props.name = "settings"
        add_shortcut.props.always_show_image = True
        add_shortcut.props.image_position = Gtk.PositionType.TOP
        add_shortcut.connect("clicked", self.on_settings_action)
        stashed_settings_grid.add(add_shortcut)

        quit_stashed = Gtk.Button(label="Quit Stashed", image=Gtk.Image().new_from_icon_name("application-exit", Gtk.IconSize.DIALOG))
        quit_stashed.props.name = "settings"
        quit_stashed.props.always_show_image = True
        quit_stashed.props.image_position = Gtk.PositionType.TOP
        quit_stashed.connect("clicked", self.on_settings_action)
        stashed_settings_grid.add(quit_stashed)

        buy_me_coffee = Gtk.Button(label="Buy Me Coffee", image=Gtk.Image().new_from_icon_name("com.github.hezral-coffee", Gtk.IconSize.DIALOG))
        buy_me_coffee.props.name = "settings"
        buy_me_coffee.props.always_show_image = True
        buy_me_coffee.props.image_position = Gtk.PositionType.TOP
        buy_me_coffee.connect("clicked", self.on_settings_action)
        stashed_settings_grid.add(buy_me_coffee)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.expand = True
        scrolled_window.add(stashed_settings_grid)

        return scrolled_window

    def on_settings_action(self, button):
        if button.props.label == "Add Shortcut":
            Gtk.show_uri_on_window(self, "settings://input/keyboard/shortcuts", GLib.get_current_time())

        if button.props.label == "Quit Stashed":
            self.destroy()
        if button.props.label == "Buy Me Coffee":
            Gtk.show_uri_on_window(None, "https://www.buymeacoffee.com/hezral", GLib.get_current_time())

    def on_stash_items_flowboxchild_activated(self, flowbox, flowboxchild):
        flowboxchild.get_children()[0].revealer.set_reveal_child(True)

    def on_stash_grid_clicked(self, widget, eventbutton):
        if eventbutton.button == 3:
            self.reveal_stash_grid()

    def on_search_clicked(self, button):
        self.reveal_stash_grid()

    def on_menu_clicked(self, button):
        if self.stack.get_visible_child() == self.stashed_settings_grid:
            self.stack.set_visible_child(self.stash_stacked_grid)
        else:
            self.stack.set_visible_child(self.stashed_settings_grid)

    def on_clear_stash(self, button):
        for flowboxchild in self.stash_flowbox.get_children():
            flowboxchild.destroy()

        for child in self.stash_stacked.get_children():
            child.destroy()

        self.search_revealer.set_reveal_child(False)
        self.clear_stash_revealer.set_reveal_child(False)
        self.header.props.title = "Stashed"

    def reveal_stash_grid(self):
        if self.stack.get_visible_child() == self.stash_flowbox_grid:
            self.stack.set_visible_child(self.stash_stacked_grid)
            if len(self.stash_flowbox.get_selected_children()) > 0:
                self.stash_flowbox.unselect_all()
                for flowboxchild in self.stash_flowbox.get_children():
                    flowboxchild.get_children()[0].revealer.set_reveal_child(False)
            self.on_stash_unfiltered()
            # self.disconnect_by_func(self.on_stash_filtered)
        else:
            self.stack.set_visible_child(self.stash_flowbox_grid)
            # self.connect("key-press-event", self.on_stash_filtered)

    def drag_and_drop_setup(self):
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.drag_dest_add_uri_targets()
        self.drag_dest_add_image_targets()
        self.connect("drag_data_received", self.on_drag_data_received)

    def drag_and_grab_setup(self, widget):
        widget.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
        widget.drag_source_add_uri_targets()
        # widget.connect("drag_data_get", self.on_drag_data_get)
        widget.connect("drag_end", self.grab_from_stash)
    
    def dnd_debug(self, *args):
        print(locals())

    def on_drag_data_get(self, widget, drag_context, data, info, timestamp):
        # print(locals())
        Gtk.drag_set_icon_widget(drag_context, self.iconstack_drag_widget, -2, -2)
        
    def on_drag_data_received(self, widget, context, x, y, data, info, timestamp):
        self.add_to_stash(data.get_target(), data)
        Gtk.drag_finish(context, True, False, timestamp) 

    def grab_from_stash(self, widget, drag_context):
        uris = []
        if isinstance(widget, Gtk.Overlay):
            for child in widget.get_children():
                if child.path != None:
                    uris.append("file://" + child.path)
                    
        else:
            for child in widget.get_selected_children():
                if child.get_children()[0].get_child().get_children()[1].path != None:
                    uris.append("file://" + child.get_children()[0].get_child().get_children()[1].path)

        uri_list = '\n'.join(uris)
        uri = 'copy' + uri_list
        
        stashed_window = self.app.utils.get_xlib_window_by_gtk_application_id(self.app.props.application_id)
        self.app.utils.copy_to_clipboard(uri)
        self.app.utils.set_active_window_by_pointer()
        self.app.utils.paste_from_clipboard()
        self.app.utils.set_active_window_by_xwindow(stashed_window)

    @run_async
    def add_to_stash(self, target, data):
        from urllib.parse import urlparse
        import time

        print(target)

        if str(target) == "text/uri-list":
            uris = data.get_uris()
            for uri in uris:
                parsed_uri = urlparse(uri)
                path, hostname = GLib.filename_from_uri(uri)
                try:
                    iconstack_child = [child for child in self.stash_stacked.get_children() if path == child.path][0]
                except:
                    if os.path.exists(path):
                        if os.path.isdir(path):  
                            mime_type = "inode/directory"
                        elif os.path.isfile(path):  
                            mime_type, val = Gio.content_type_guess(path, data=None)

                    GLib.idle_add(self.update_stash, path, mime_type)
                    # self.update_stash(path, mime_type)
                    time.sleep(0.05)

    def update_stash(self, path, mime_type):
        icon = DefaultContainer(path, mime_type, self.app)
        item = DefaultContainer(path, mime_type, self.app, 64)
        if "image" in mime_type and not "gif" in mime_type:
            try:
                icon = ImageContainer(path)
                item = ImageContainer(path, 64)
            except:
                pass
        if "gif" in mime_type:
            icon = GifContainer(path)
            item = GifContainer(path, 64)


        import random
        if len(self.stash_stacked.get_children()) != 1:
            margin = random.randint(24,64) + self.iconstack_offset
            set_margins = [icon.set_margin_bottom, icon.set_margin_top, icon.set_margin_left, icon.set_margin_right]
            random.choice(set_margins)(margin)
            random.choice(set_margins)(self.iconstack_offset + random.randint(10,1000) % 2)

        self.stash_stacked.add_overlay(icon)

        self.stash_flowbox.add(StashItem(path, item))

        if self.iconstack_offset >= 30:
            self.iconstack_offset = 0
        else:
            self.iconstack_offset += 2

        self.header.props.title = "{count} Stashed".format(count=len(self.stash_stacked.get_children()))
        self.stash_stacked.show_all()
        self.stash_flowbox.show_all()
        self.search_revealer.set_reveal_child(True)
        self.clear_stash_revealer.set_reveal_child(True)

    def filter_func(self, flowboxchild, search_text):
        stash_item_path = os.path.basename(flowboxchild.get_children()[0].get_child().get_children()[1].path)
        if search_text in stash_item_path:
            return True
        else:
            return False

    def on_stash_unfiltered(self, *args):
        self.stash_flowbox.invalidate_filter()
        self.stash_flowbox.set_filter_func(self.filter_func, "")
        self.search = []
        self.stash_flowbox.unselect_all()
        self.search_keyword_revealer.set_reveal_child(False)
        self.clear_keyword_revealer.set_reveal_child(False)
        
    def on_stash_filtered(self, window, eventkey):

        key = Gdk.keyval_name(eventkey.keyval).lower()
        key_length = len(key)
        
        # filter = False

        if len(self.stash_stacked.get_children()) != 0:

            if ('GDK_SHIFT_MASK' in eventkey.state.value_names and 'GDK_MOD2_MASK' in eventkey.state.value_names) and key == "backspace":
                if self.stack.get_visible_child() == self.stash_flowbox_grid:
                    self.on_stash_unfiltered()
                    self.reveal_stash_grid()

            elif (len(eventkey.state.value_names) == 1 and 'GDK_MOD2_MASK' in eventkey.state.value_names) and key == "backspace":
                self.on_stash_unfiltered()
            
            elif key_length == 1:
                if self.stack.get_visible_child() != self.stash_flowbox_grid:
                    self.reveal_stash_grid()
                self.trigger_stash_filter(key)
                print(key, len(key), Gdk.keyval_name(eventkey.keyval), eventkey.keyval, eventkey.state.value_names)

    def trigger_stash_filter(self, key):
        self.search_keyword_revealer.set_reveal_child(True)
        self.clear_keyword_revealer.set_reveal_child(True)
        self.search.append(key)
        keyword = ''.join(self.search)
        self.stash_flowbox.invalidate_filter()
        self.stash_flowbox.set_filter_func(self.filter_func, keyword)
        self.search_keyword.props.label = keyword

    def hide_on_close_window(self, window, event):
        self.hide()
        self.on_stash_unfiltered()
        self.stack.set_visible_child(self.stash_stacked_grid)
        return True

class StashItem(Gtk.EventBox):
    def __init__(self, filepath, item, *args, **kwargs):
        super().__init__(*args, **kwargs)

        button = Gtk.Button(image=Gtk.Image().new_from_icon_name("process-completed", Gtk.IconSize.SMALL_TOOLBAR))
        button.set_size_request(32, 32)
        button.props.name = "stash-item-select"
        button.props.halign = Gtk.Align.END
        button.props.valign = Gtk.Align.START
        button.props.can_focus = False
        button.connect("clicked", self.on_select_button)
        button.get_style_context().add_class("stash-item-select")
        self.revealer = Gtk.Revealer()
        self.revealer.add(button)

        label = ItemLabel(filepath)

        grid = Gtk.Grid()
        grid.props.margin = 6
        grid.props.row_spacing = 4
        grid.props.expand = True
        grid.props.halign = grid.props.valign = Gtk.Align.CENTER
        grid.attach(self.revealer, 0, 0, 1, 1)
        grid.attach(item, 0, 0, 1, 1)
        grid.attach(label, 0, 1, 1, 1)
        grid.set_size_request(100, 100)

        self.add(grid)
        self.props.has_tooltip = True
        self.props.tooltip_text = filepath

    def on_select_button(self, button):
        if self.revealer.get_reveal_child():
            self.revealer.set_reveal_child(False)
            self.get_toplevel().stash_flowbox.unselect_child(self.get_parent())


class ItemLabel(Gtk.Label):
    def __init__(self, filepath, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.label = os.path.basename(filepath)
        self.props.wrap_mode = Pango.WrapMode.CHAR
        self.props.max_width_chars = 16
        self.props.wrap = True
        self.props.hexpand = True
        self.props.justify = Gtk.Justification.CENTER
        self.props.lines = 2
        self.props.ellipsize = Pango.EllipsizeMode.END


class DefaultContainer(Gtk.Grid):
    def __init__(self, filepath, mime_type, app, size=96, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "stash-container"
        self.props.expand = True
        self.path  = filepath
        self.props.halign = self.props.valign = Gtk.Align.CENTER

        icon_size = size
        icon = Gtk.Image()

        icons = Gio.content_type_get_icon(mime_type)
        for icon_name in icons.to_string().split():
            if icon_name != "." and icon_name != "GThemedIcon":
                try:
                    icon_pixbuf = app.icon_theme.load_icon(icon_name, icon_size, 0)
                    break
                except:
                    pass
            if "generic" in icon_name:
                try:
                    icon_pixbuf = app.icon_theme.load_icon(icon_name, icon_size, 0)
                    break
                except:
                    icon_pixbuf = app.icon_theme.load_icon("application-octet-stream", icon_size, 0)
        icon.props.pixbuf = icon_pixbuf
        
        self.attach(icon, 0, 0, 1, 1)


class ImageContainer(Gtk.Grid):
    def __init__(self, filepath, size=128, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "stash-container"
        self.props.expand = True
        self.path = filepath
        self.props.halign = self.props.valign = Gtk.Align.CENTER

        icon_size = size
        icon = Gtk.Image()
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filepath, icon_size, icon_size)
        icon.props.pixbuf = icon_pixbuf

        self.attach(icon, 0, 0, 1, 1)


class GifContainer(Gtk.Grid):
    def __init__(self, filepath, size=128, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "stash-container"
        self.path = filepath

        self.pixbuf_original = GdkPixbuf.PixbufAnimation.new_from_file(filepath)
        self.pixbuf_original_height = self.pixbuf_original.get_height()
        self.pixbuf_original_width = self.pixbuf_original.get_width()
        self.iter = self.pixbuf_original.get_iter()
        for i in range(0, 250):
            timeval = GLib.TimeVal()
            timeval.tv_sec = int(str(GLib.get_real_time())[:-3])
            self.iter.advance(timeval)
            self.queue_draw()

        self.ratio_h_w = self.pixbuf_original_height / self.pixbuf_original_width
        self.ratio_w_h = self.pixbuf_original_width / self.pixbuf_original_height

        if self.ratio_w_h > 1:
            self.set_size_request(size, int((10/16)*size) + 1)
        else:
            self.set_size_request(size, size)
    
        drawing_area = Gtk.DrawingArea()
        drawing_area.props.expand = True
        drawing_area.props.halign = drawing_area.props.valign = Gtk.Align.FILL
        drawing_area.connect("draw", self.draw)
        drawing_area.props.can_focus = False

        self.attach(drawing_area, 0, 0, 1, 1)
        self.props.halign = self.props.valign = Gtk.Align.CENTER
        
        # self.animation_loop_func()
        
    def animation_loop_func(self, *args):
        self.iter.advance()
        GLib.timeout_add(self.iter.get_delay_time(), self.animation_loop_func, None)
        self.queue_draw()

    def draw(self, drawing_area, cairo_context, hover_scale=1):
        '''
        Forked and ported from https://github.com/elementary/greeter/blob/master/src/Widgets/BackgroundImage.vala
        '''
        from math import pi

        scale = self.get_scale_factor()
        width = self.get_allocated_width() * scale * hover_scale
        height = self.get_allocated_height() * scale * hover_scale
        radius = 4 * scale #Off-by-one to prevent light bleed

        pixbuf = GdkPixbuf.PixbufAnimationIter.get_pixbuf(self.iter)
        pixbuf_fitted = GdkPixbuf.Pixbuf.new(pixbuf.get_colorspace(), pixbuf.get_has_alpha(), pixbuf.get_bits_per_sample(), width, height)

        if int(width * self.ratio_h_w) < height:
            scaled_pixbuf = pixbuf.scale_simple(int(height * self.ratio_w_h), height, GdkPixbuf.InterpType.BILINEAR)
        else:
            scaled_pixbuf = pixbuf.scale_simple(width, int(width * self.ratio_h_w), GdkPixbuf.InterpType.BILINEAR)

        if self.pixbuf_original_width * self.pixbuf_original_height < width * height:
            # Find the offset we need to center the source pixbuf on the destination since its smaller
            y = abs((height - self.pixbuf_original_height) / 2)
            x = abs((width - self.pixbuf_original_width) / 2)
            final_pixbuf = self.pixbuf_original
        else:
            # Find the offset we need to center the source pixbuf on the destination
            y = abs((height - scaled_pixbuf.props.height) / 2)
            x = abs((width - scaled_pixbuf.props.width) / 2)
            scaled_pixbuf.copy_area(x, y, width, height, pixbuf_fitted, 0, 0)
            # Set coordinates for cairo surface since this has been fitted, it should be (0, 0) coordinate
            x = y = 0
            final_pixbuf = pixbuf_fitted

        cairo_context.save()
        cairo_context.scale(1.0 / scale, 1.0 / scale)
        cairo_context.new_sub_path()

        # draws rounded rectangle
        cairo_context.arc(width - radius, radius, radius, 0-pi/2, 0) # top-right-corner
        cairo_context.arc(width - radius, height - radius, radius, 0, pi/2) # bottom-right-corner
        cairo_context.arc(radius, height - radius, radius, pi/2, pi) # bottom-left-corner
        cairo_context.arc(radius, radius, radius, pi, pi + pi/2) # top-left-corner
    
        cairo_context.close_path()

        Gdk.cairo_set_source_pixbuf(cairo_context, final_pixbuf, x, y)

        cairo_context.clip()
        cairo_context.paint()
        cairo_context.restore()