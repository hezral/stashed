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


old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')


def mousepos():
    """mousepos() --> (x, y) get the mouse coordinates on the screen"""
    display = Gdk.Display.get_default()
    seat = display.get_default_seat()
    pointer = seat.get_pointer()
    position = pointer.get_position()
    position_text = "x: " + str(position[1]) + " y: " + str(position[2])
    return position_text

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
            time.sleep(0.15)

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