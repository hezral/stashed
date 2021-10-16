<div align="center">

![icon](data/icons/128.svg)

</div>

If you like what i make, it would really be nice to have someone buy me a coffee
<div align="center">
<a href="https://www.buymeacoffee.com/hezral" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>
</div>

### Drag your files to Stashed to copy it later
* Collect files from multiple directory
* Copy all files in the stash to a direction
* Copy individual files by selecting what you want
* Shake the mouse cursor to call Stashed

<div align="center">

![Screenshot](data/screenshot-01.png?raw=true)

</div>

# Installation

## Build using flatpak
* requires that you have flatpak-builder installed
* flatpak enabled
* flathub remote enabled

```
flatpak-builder --user --force-clean --install build-dir com.github.hezral.stashed.yml
```

### Build using meson 
Ensure you have these dependencies installed

* python3
* python3-gi
* libgranite-dev
* python-xlib
* xclip
* pynput

Download the updated source [here](https://github.com/hezral/stashed/archive/master.zip), or use git:
```bash
git clone https://github.com/hezral/stashed.git
cd clips
meson build --prefix=/usr
cd build
ninja build
sudo ninja install
```
The desktop launcher should show up on the application launcher for your desktop environment
if it doesn't, try running
```
com.github.hezral.stashed
```

# Thanks/Credits
- [ElementaryPython](https://github.com/mirkobrombin/ElementaryPython) This started me off on coding with Python and GTK
- [Lazka's PyGObject API Reference](https://https://lazka.github.io) The best documentation site for coding with Python and GTK