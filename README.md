# Futurama-Tools

*Tools to analyze files of [the video-game "Futurama" (2003)](https://en.wikipedia.org/wiki/Futurama_(video_game)).*

---

## Motivation

After watching [a video by oddheader](https://youtu.be/bgcHH4v0DjQ?t=22), about [an undiscovered easter-egg in Futurama](https://tcrf.net/Futurama#Easter_Egg), I wondered if I could figure it out.
I was initially going to use Xbox emulation and a debugger, but I quickly decided to take a different approach (pure file analysis, no debugging).

## Existing tools

### Scripts: ful / dbg

The first project was a simple disassembler for the "ful" files (which are scripts).
I got stuck during development, so I added a parser for "dbg" files (which are debug symbols).
Eventually that lead to proper "ful" disassembly.
The disassembly is still hard to read (it's stack based), so I *might* work on an optimizer to make it more readable in the distant future.

### Archives: img

I had originally used [Game Extractor](http://www.watto.org/game_extractor.html) to extract the "ful" and "dbg" files from "img" files, but it's lacking the directory layout.
Hence, I used the [information on the Xentax Wiki](http://wiki.xentax.com/index.php/Futurama_XBox_IMG) to write my own script for "img" extraction.

### Media: nif

Later, I added support "nif" support, by extending nif.xml for [NifTools (including blender-plugin)](https://github.com/niftools/blender_nif_plugin).
The [modified nif.xml (base version 0.9) can be found in my futurama-tools-nifxml repository](https://github.com/JayFoxRox/futurama-tools-nifxml/).
You'll need `pip install --user -U git+https://github.com/neomonkeus/pyffi.git@hfloat`.

I quickly gave up on this, because:

* `nifskope` uses nif.xml 0.9 and newer.
* `blender_nif_plugin` has no full Blender 2.80 support yet, and it was buggy.
* `pyffi` uses nif.xml 0.7 and older.

`nifskope` is harder to debug and didn't even compile out-of-the-box.
Meanwhile, `blender_nif_plugin` also didn't work. And while the underlying `pyffi` works, it only supports very old nif.xml.
`nifskope` also handles these old nif.xml, but it still isn't fully compatible.
So I wouldn't be able to support both tools at the same time and working on upstream would be an issue due to my old nif.xml base.

If you still want to try the nif support, just run blender using `NIFXMLPATH=$(pwd) blender` from the futurama-tools-nifxml path.
I made a small tool for inspection, which can be ran using `NIFXMLPATH="$(pwd)" ../futurama-tools/inspect_nif.py FutPAL00/levels/level1-1/stage1.nif`.
For `nifskope`, just copy the nif.xml from futurama-tools-nifxml, to your `nifskope` path.

### Translations: ldb

I added support for "ldb" files, so I could understand the mission plot more easily.

### Fonts: fnt

I also added support for "fnt" files for completeness.
The "fonts/latin1_xbox.fnt" shipped with the game appears to be broken.

## State of repository

The tools are very incomplete and not very functional.
I have never played the game and I probably won't maintain these tools.

I don't know if these tools work for the PS2 version, I've looked at the Xbox version exclusively.

If you want to know how these formats work, or how to use the tools, simply read the source-code.

## Donate

If you like my work, a donation would be nice:

* [Patreon](https://www.patreon.com/jayfoxrox)
* [PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=x1f3o3x7x%40googlemail%2ecom&lc=GB&item_name=Jannik%20Vogel%20%28JayFoxRox%29&no_note=0&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHostedGuest)

Even a small amount does help me and shows appreciation. Thank you!

---

**(C)2019 [Jannik Vogel](http://jannikvogel.de/)**

*All rights reserved.*
