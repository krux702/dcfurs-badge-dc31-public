# DEF CON Furs 2023 Badge 

# krux's update to ventorvar's boop nonsense

This is not a full source/build, but meant two files you can update that adds initial boop support. Get it going with something like:

```
rshell rsync ./src /
rshell "repl ~ import machine ~ machine.soft_reset() ~"
```

You can also make use of Adafruit's `ampy` utility to write changes:

```
ampy --port /dev/ttyACM0 put main.py
ampy --port /dev/ttyACM0 put touch.py
ampy --port /dev/ttyACM0 put config
```

## Schematic

The Schematic is located in this PDF: [DCF31BadgeSchematic.pdf](https://github.com/defconfurs/dcfurs-badge-dc31-public/blob/main/DCF31BadgeSchematic.pdf)


## Bill of Materials

The BoM is on Google Sheets:  https://docs.google.com/spreadsheets/d/1LJeAcxZYNxy8RmYSu6KfBTrNyNzvA-suKKZmO6_C-Eg/edit?usp=sharing

## Builds Folder

### OSD.ino.uf2

This is an LED test for the badge.

### OSDColour.ino.uf2

We had issues with the OSD.ino program not detecting shorted LEDs, so this is a test program that works better at that.

### OSDColour500.ino.uf2

Same as above, just faster.

### DCFurs31_initial.ino.uf2

This is the initial release firmware on the badges.


### firmware.uf2 

This is the new MicroPython firmware.


### flash_nuke.uf2

Use only if you really mess up and send your badge into a boot loop because of 
bad python code that is preventing the upload new code before the badge resets 
itself. Use this to wipe out the flash used for MicroPython program storage,
then re-flash the badge with the MicroPython firmware.
