#!/usr/bin/python3
import Xlib
import Xlib.display

disp = Xlib.display.Display()
root = disp.screen().root

NET_WM_NAME = disp.intern_atom('_NET_WM_NAME')
NET_ACTIVE_WINDOW = disp.intern_atom('_NET_ACTIVE_WINDOW')
NET_CLIENT_LIST = disp.intern_atom('_NET_CLIENT_LIST')
GTK_APPLICATION_ID = disp.intern_atom('_GTK_APPLICATION_ID')

root.change_attributes(event_mask=Xlib.X.FocusChangeMask)
# while True:
try:
    window_id = root.get_full_property(NET_CLIENT_LIST, Xlib.X.AnyPropertyType).value
    for id in window_id:
        window = disp.create_resource_object('window', id)
        window.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
        if window.get_full_property(GTK_APPLICATION_ID, 0):
            if window.get_full_property(GTK_APPLICATION_ID, 0).value.decode("utf-8") == "com.github.hezral.stashed":
                break

except Xlib.error.XError: #simplify dealing with BadWindow
    window_name = None
# print(window_name)
# print(type(window))
# window_name = None
    # event = disp.next_event()

print(window.get_full_property(GTK_APPLICATION_ID, 0).value.decode("utf-8"))
print(type(window))