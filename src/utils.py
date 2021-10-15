# utils.py
#
# Copyright 2021 adi
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

class HelperUtils:
    @staticmethod
    def run_async(func):
        '''
        https://github.com/learningequality/ka-lite-gtk/blob/341813092ec7a6665cfbfb890aa293602fb0e92f/kalite_gtk/mainwindow.py
        http://code.activestate.com/recipes/576683-simple-threading-decorator/
        run_async(func): 
        function decorator, intended to make "func" run in a separate thread (asynchronously).
        Returns the created Thread object
        Example:
            @run_async
            def task1():
                do_something
            @run_async
            def task2():
                do_something_too
        '''
        from threading import Thread
        from functools import wraps

        @wraps(func)
        def async_func(*args, **kwargs):
            func_hl = Thread(target=func, args=args, kwargs=kwargs)
            func_hl.start()
            # Never return anything, idle_add will think it should re-run the
            # function because it's a non-False value.
            return None

        return async_func

    @staticmethod
    def get_window_by_gtk_application_id_xlib(gtk_application_id):
        ''' Function to get window using the gtk_application_id from NET_WM '''
        import Xlib
        import Xlib.display

        display = Xlib.display.Display()
        root = display.screen().root

        NET_CLIENT_LIST = display.intern_atom('_NET_CLIENT_LIST')
        GTK_APPLICATION_ID = display.intern_atom('_GTK_APPLICATION_ID')

        root.change_attributes(event_mask=Xlib.X.FocusChangeMask)
        try:
            window_id = root.get_full_property(NET_CLIENT_LIST, Xlib.X.AnyPropertyType).value
            for id in window_id:
                window = display.create_resource_object('window', id)
                window.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
                if window.get_full_property(GTK_APPLICATION_ID, 0):
                    if window.get_full_property(GTK_APPLICATION_ID, 0).value.decode("utf-8") == gtk_application_id:
                        break

        except Xlib.error.XError: #simplify dealing with BadWindow
            window = None

        return window

    @staticmethod
    def get_active_window_xlib():
        ''' Function to get active window '''
        import Xlib
        import Xlib.display

        display = Xlib.display.Display()
        root = display.screen().root

        NET_ACTIVE_WINDOW = display.intern_atom('_NET_ACTIVE_WINDOW')

        root.change_attributes(event_mask=Xlib.X.FocusChangeMask)
        try:
            window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
            window = display.create_resource_object('window', window_id)
        except Xlib.error.XError: #simplify dealing with BadWindow
            window = None

        return window

    @staticmethod
    def get_window_id_by_gtk_application_id_xlib(gtk_application_id):
        ''' Function to get window using the gtk_application_id from NET_WM '''
        import Xlib
        import Xlib.display

        display = Xlib.display.Display()
        root = display.screen().root

        NET_CLIENT_LIST = display.intern_atom('_NET_CLIENT_LIST')
        GTK_APPLICATION_ID = display.intern_atom('_GTK_APPLICATION_ID')

        root.change_attributes(event_mask=Xlib.X.FocusChangeMask)
        try:
            window_ids = root.get_full_property(NET_CLIENT_LIST, Xlib.X.AnyPropertyType).value
            for window_id in window_ids:
                window = display.create_resource_object('window', window_id)
                window.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
                if window.get_full_property(GTK_APPLICATION_ID, 0):
                    if window.get_full_property(GTK_APPLICATION_ID, 0).value.decode("utf-8") == gtk_application_id:
                        break

        except Xlib.error.XError: #simplify dealing with BadWindow
            window_id = None

        return window_id

    @staticmethod
    def get_active_window_id_xlib():
        ''' Function to get active window '''
        import Xlib
        import Xlib.display

        display = Xlib.display.Display()
        root = display.screen().root

        NET_ACTIVE_WINDOW = display.intern_atom('_NET_ACTIVE_WINDOW')

        root.change_attributes(event_mask=Xlib.X.FocusChangeMask)
        try:
            window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
        except Xlib.error.XError: #simplify dealing with BadWindow
            window_id = None

        return window_id

    @staticmethod
    def set_active_window_by_pointer():
        ''' Function to set window as active based on where the mouse pointer is located '''
        import Xlib
        from Xlib.display import Display
        from Xlib import X

        display = Display()
        root = display.screen().root
        window = root.query_pointer().child
        window.set_input_focus(X.RevertToParent, X.CurrentTime)
        window.configure(stack_mode=X.Above)
        display.sync()

        # get active window
        NET_ACTIVE_WINDOW = display.intern_atom('_NET_ACTIVE_WINDOW')
        try:
            window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
        except Xlib.error.XError: #simplify dealing with BadWindow
            window_id = None

        return window_id

    @staticmethod
    def set_active_window_by_xwindow(window):
        ''' Function to set window as active based on xid '''
        import Xlib
        from Xlib.display import Display
        from Xlib import X

        display = Display()
        window.set_input_focus(X.RevertToParent, X.CurrentTime)
        window.configure(stack_mode=X.Above)
        display.sync()

    @staticmethod
    def get_active_window_application_id():
        ''' Function to get active window '''
        import Xlib
        import Xlib.display

        display = Xlib.display.Display()
        root = display.screen().root

        NET_ACTIVE_WINDOW = display.intern_atom('_NET_ACTIVE_WINDOW')
        GTK_APPLICATION_ID = display.intern_atom('_GTK_APPLICATION_ID')

        root.change_attributes(event_mask=Xlib.X.FocusChangeMask)
        try:
            window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
            window = display.create_resource_object('window', window_id)
            try:
                return window.get_full_property(GTK_APPLICATION_ID, 0).value.replace(b'\x00',b' ').decode("utf-8").lower()
            except:
                return None
        except Xlib.error.XError: #simplify dealing with BadWindow
            return None

    @staticmethod
    def get_active_window_wm_class():
        ''' Function to get active window '''
        import Xlib
        import Xlib.display

        display = Xlib.display.Display()
        root = display.screen().root

        NET_ACTIVE_WINDOW = display.intern_atom('_NET_ACTIVE_WINDOW')
        WM_CLASS = display.intern_atom('WM_CLASS')

        root.change_attributes(event_mask=Xlib.X.FocusChangeMask)
        try:
            window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
            window = display.create_resource_object('window', window_id)
            try:
                return window.get_full_property(WM_CLASS, 0).value.replace(b'\x00',b' ').decode("utf-8").lower()
            except:
                return None
        except Xlib.error.XError: #simplify dealing with BadWindow
            return None

    @staticmethod
    def copy_to_clipboard(clipboard_target, file, type=None):
        ''' Function to copy files to clipboard '''
        from subprocess import Popen, PIPE

        try:
            if "url" in type:
                with open(file) as _file:
                    data = Popen(['echo', _file.readlines()[0].rstrip("\n").rstrip("\n")], stdout=PIPE)
                    Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target], stdin=data.stdout)
            else:
                Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target, '-i', file])
            return True
        except:
            return False

    @staticmethod
    def copy_files_to_clipboard(uris):
        ''' Function to copy files to clipboard from a string of uris in file:// format '''
        from subprocess import Popen, PIPE
        try:
            copyfiles = Popen(['xclip', '-selection', 'clipboard', '-target', 'x-special/gnome-copied-files'], stdin=PIPE)
            copyfiles.communicate(str.encode(uris))
            return True
        except:
            return False

    @staticmethod
    def paste_from_clipboard():
        '''
        Function to paste from clipboard based on where the mouse pointer is hovering
        '''
        # ported from Clipped: https://github.com/davidmhewitt/clipped/blob/edac68890c2a78357910f05bf44060c2aba5958e/src/ClipboardManager.vala
        import time

        def perform_key_event(accelerator, press, delay):
            import Xlib
            from Xlib import X
            from Xlib.display import Display
            from Xlib.ext.xtest import fake_input
            from Xlib.protocol.event import KeyPress, KeyRelease
            import time

            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk, Gdk, GdkX11

            keysym, modifiers = Gtk.accelerator_parse(accelerator)
            display = Display()
            # root = display.screen().root
            # window = root.query_pointer().child
            # window.set_input_focus(X.RevertToParent, X.CurrentTime)
            # window.configure(stack_mode=X.Above)
            # display.sync()

            keycode = display.keysym_to_keycode(keysym)

            if press:
                event_type = X.KeyPress
            else:
                event_type = X.KeyRelease

            if keycode != 0:
                if 'GDK_CONTROL_MASK' in modifiers.value_names:
                    modcode = display.keysym_to_keycode(Gdk.KEY_Control_L)
                    fake_input(display, event_type, modcode, delay)

                if 'GDK_SHIFT_MASK' in modifiers.value_names:
                    modcode = display.keysym_to_keycode(Gdk.KEY_Shift_L)
                    fake_input(display, event_type, modcode, delay)

                fake_input(display, event_type, keycode, delay)
                display.sync()

        perform_key_event("<Control>v", True, 100)
        perform_key_event("<Control>v", False, 0)

