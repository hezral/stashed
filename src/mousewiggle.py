#!/usr/bin/env python
# I didn't write this
# many examples exist on StackOverflow, etc..
# 
# Note: you'll need python-xlib, python-Gtk
# sudo apt-get install python-xlib python-Gtk2
#

import sys
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

import time
import threading
from datetime import datetime


old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

SHAKE_DIST = 20
SHAKE_SLICE_TIMEOUT = 75 # ms
SHAKE_TIMEOUT = 500 # ms
SHOWING_TIMEOUT = 750 #ms
needed_shake_count = 4

SENSITIVITY_HIGH = 2
SENSITIVITY_MEDIUM = 4
SENSITIVITY_LOW = 7

showing_timestamp = datetime.now()
shake_slice_timestamp = datetime.now()
shake_timeout_timestamp = datetime.now()
shake_count = 0

new_x = 0
old_x = 0
min_x = 0
max_x = 0
has_min = 0
has_max = 0

def mousepos():
    """mousepos() --> (x, y) get the mouse coordinates on the screen"""
    display = Gdk.Display.get_default()
    seat = display.get_default_seat()
    pointer = seat.get_pointer()
    position = pointer.get_position()
    return position

class MouseThread(threading.Thread):
    def __init__(self, parent, label):
        threading.Thread.__init__(self)
        self.label = label
        self.killed = False

    def run(self):
        try:
            self.run_thread()
        except (KeyboardInterrupt, SystemExit):
            # sys.exit()
            self.run_thread()

    def run_thread(self):
        while True:
            if self.stopped():
                break
            position = mousepos()

            GLib.idle_add(self.label.set_text, position)
            # print(datetime.now(), position)
            time.sleep(0.2)

    def kill(self):
        self.killed = True

    def stopped(self):
        return self.killed

class PyApp(Gtk.Window):

    def __init__(self):
        super().__init__()

        self.set_title("Mouse coordinates 0.1")
        self.connect("destroy", self.quit)

        label = Gtk.Label()

        self.mouseThread = MouseThread(self, label)
        self.mouseThread.start()

        fixed = Gtk.Fixed()
        fixed.props.halign = fixed.props.valign = Gtk.Align.CENTER
        fixed.put(label, 10, 10)

        self.set_size_request(200, 200)
        self.add(fixed)
        self.show_all()

    def quit(self, widget):
        self.mouseThread.kill()
        Gtk.main_quit()


if __name__ == '__main__':
    app = PyApp()
    Gtk.main()