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
from gi.repository import Gtk, Handy, Gdk, Gio, Granite, GLib, GdkPixbuf

IMAGE_DND_TARGET = Gtk.TargetEntry.new('image/png', Gtk.TargetFlags.SAME_APP, 0)
UTF8TEXT_DND_TARGET = Gtk.TargetEntry.new('text/plain;charset=utf-8', Gtk.TargetFlags.SAME_APP, 0)
PLAINTEXT_DND_TARGET = Gtk.TargetEntry.new('text/plain', Gtk.TargetFlags.SAME_APP, 0)
URI_DND_TARGET = Gtk.TargetEntry.new('text/uri-list', Gtk.TargetFlags.SAME_APP, 0)

class StashedWindow(Handy.Window):
    __gtype_name__ = 'StashedWindow'

    iconstack_offset = 0

    Handy.init()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.header = Handy.HeaderBar()
        self.header.props.show_close_button = True
        self.header.props.hexpand = True
        self.header.props.title = "Stashed"
        self.header.props.show_close_button = True
        self.header.props.decoration_layout = "close:"
        self.header.get_style_context().add_class(Granite.STYLE_CLASS_DEFAULT_DECORATION)
        self.header.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)

        self.iconstack_overlay = Gtk.Overlay()
        self.iconstack_overlay.props.expand = True
        self.iconstack_overlay.props.valign = self.iconstack_overlay.props.halign = Gtk.Align.FILL
        
        self.stash_grid = Gtk.Grid()
        self.stash_grid.attach(self.iconstack_overlay, 0, 0, 1, 1)

        self.grid = Gtk.Grid()
        self.grid.props.expand = True
        self.grid.attach(self.header, 0, 0, 1, 1)
        self.grid.attach(self.stash_grid, 0, 1, 1, 1)

        self.add(self.grid)
        self.props.resizable = False
        self.show_all()
        self.set_keep_above(True)
        self.set_size_request(360, 360)
        self.app = self.props.application

        self.drag_and_drop_setup()
        self.drag_and_grab_setup()

    def drag_and_drop_setup(self):
        self.drag_dest_set(Gtk.DestDefaults.ALL, [URI_DND_TARGET], Gdk.DragAction.COPY)
        self.drag_dest_add_uri_targets()
        self.drag_dest_add_image_targets()
        self.drag_dest_add_text_targets()
        self.connect("drag_data_received", self.on_drag_data_received)

    def drag_and_grab_setup(self):
        self.iconstack_overlay.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [URI_DND_TARGET], Gdk.DragAction.COPY)
        self.iconstack_overlay.drag_source_add_uri_targets()
        self.iconstack_overlay.connect("drag_data_get", self.on_drag_data_get)
    
    def on_drag_data_get(self, widget, context, data, info, timestamp):
        print(locals())
        self.grab_from_stash(data.get_target(), data)
        # Gtk.drag_finish(context, True, False, timestamp)
        
    def on_drag_data_received(self, widget, context, x, y, data, info, timestamp):
        # print(context.get_source_window())
        self.add_to_stash(data.get_target(), data)
        Gtk.drag_finish(context, True, False, timestamp) 
    
    def remove_from_stash(self, target, data):
        print(locals())

    def grab_from_stash(self, target, data):
        print(target, data)
        # if str(target) == "text/uri-list":
        #     uris = data.get_uris()
        #     file_count = len(uris)
        #     i = 0
        #     for uri in uris:

    def add_to_stash(self, target, data):
        from urllib.parse import urlparse
        
        print(target, data.get_data_type())
        print(data.get_text())

        mime_type = "application/octet-stream"

        if str(target) == "text/uri-list":
            uris = data.get_uris()
            file_count = len(uris)
            i = 0
            for uri in uris:
                parsed_uri = urlparse(uri)
                path, hostname = GLib.filename_from_uri(uri)
                path_type = "local"
                if parsed_uri.scheme == "":
                    path = parsed_uri.netloc
                try:
                    iconstack_child = [child for child in self.iconstack_overlay.get_children() if path.replace("/", "_") == child.props.name][0]
                except:
                    if os.path.exists(path):
                        if os.path.isdir(path):  
                            mime_type = "inode/directory"
                        elif os.path.isfile(path):  
                            mime_type, val = Gio.content_type_guess(path, data=None)
                        self.update_stash(i, path, mime_type)
                        i += 1

    def update_stash(self, i, path, mime_type):
        icon_size = 96
        icon = None
        icons = Gio.content_type_get_icon(mime_type)
        icon = Gtk.Image()
        icon.props.halign = Gtk.Align.CENTER

        if "image" in mime_type and not "gif" in mime_type:
            icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, icon_size, icon_size)
            icon.props.pixbuf = icon_pixbuf
        elif "gif" in mime_type:
            icon = GifContainer(path)
            icon.get_style_context().add_class("iconstack-gif")
        else:
            for icon_name in icons.to_string().split():
                if icon_name != "." and icon_name != "GThemedIcon":
                    try:
                        icon_pixbuf = self.app.icon_theme.load_icon(icon_name, icon_size, 0)
                        icon.props.pixbuf = icon_pixbuf
                        break
                    except:
                        pass

        icon.props.name = path.replace("/","_")

        children_count = len(self.iconstack_overlay.get_children())
        self.iconstack_overlay.add_overlay(icon)

        # margin = 72 + self.iconstack_offset

        import random
        margin = random.randint(16,64) + self.iconstack_offset
        set_margins = [icon.set_margin_bottom, icon.set_margin_top, icon.set_margin_left, icon.set_margin_right]
        random.choice(set_margins)(margin)
        random.choice(set_margins)(self.iconstack_offset + random.randint(10,1000) % 2)

        i += 1
        if self.iconstack_offset >= 40:
            self.iconstack_offset = 0
        else:
            self.iconstack_offset += 2

        self.header.props.title = "{count} Stashed".format(count=len(self.iconstack_overlay.get_children()))
        self.stash_grid.show_all()



class StashContainer(Gtk.Grid):
    def __init__(self, filepath, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "stash-containernon"

        icon_size = 96
        icon = None
        icon = Gtk.Image()
        icon.props.halign = Gtk.Align.CENTER

        self.attach(icon, 0, 0, 1, 1)
        

class GifContainer(Gtk.Grid):
    def __init__(self, filepath, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pixbuf_original = GdkPixbuf.PixbufAnimation.new_from_file(filepath)
        self.pixbuf_original_height = self.pixbuf_original.get_height()
        self.pixbuf_original_width = self.pixbuf_original.get_width()
        self.iter = self.pixbuf_original.get_iter()
        for i in range(0, 500):
            timeval = GLib.TimeVal()
            timeval.tv_sec = int(str(GLib.get_real_time())[:-3])
            self.iter.advance(timeval)
            self.queue_draw()

        self.ratio_h_w = self.pixbuf_original_height / self.pixbuf_original_width
        self.ratio_w_h = self.pixbuf_original_width / self.pixbuf_original_height

        if self.ratio_w_h > 1:
            self.set_size_request(100, 64)
        else:
            self.set_size_request(100, 100)
    
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