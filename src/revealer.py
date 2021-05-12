#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk

def reveal_child(button):
    if revealer.get_reveal_child():
        revealer.set_reveal_child(False)
        # this line was a mistake
        #revealer.get_reveal_child().set_visible(False)
        # revealer.set_visible(False)
    else:
        revealer.set_reveal_child(True)
        # this line was a mistake
        #revealer.get_reveal_child().set_visible(True)
        # revealer.set_visible(True)

window = Gtk.Window()
window.connect("destroy", Gtk.main_quit)

grid = Gtk.Grid()
window.add(grid)

revealer = Gtk.Revealer()
revealer.set_reveal_child(False)
grid.attach(revealer, 0, 1, 1, 1)

label = Gtk.Label("Label contained in a Revealer widget")
revealer.add(label)

button = Gtk.Button("Reveal")
button.connect("clicked", reveal_child)
grid.attach(button, 0, 0, 1, 1)

window.show_all()

Gtk.main()