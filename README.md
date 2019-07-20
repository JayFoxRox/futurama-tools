# Futurama-Tools

*Tools to analyze files of [the video-game "Futurama" (2003)](https://en.wikipedia.org/wiki/Futurama_(video_game)).*

---

## Motivation

After watching [a video by oddheader](https://youtu.be/bgcHH4v0DjQ?t=22), about [an undiscovered easter-egg in Futurama](https://tcrf.net/Futurama#Easter_Egg), I wondered if I could figure it out.
I was initially going to use Xbox emulation and a debugger, but I quickly decided to take a different approach (pure file analysis, no debugging).

## Existing tools

The first project was a simple disassembler for the "ful" files (which are scripts).
I got stuck during development, so I added a parser for "dbg" files (which are debug symbols).
Eventually that lead to proper "ful" disassembly.
The disassembly is still hard to read (it's stack based), so I *might* work on an optimizer to make it more readable in the distant future.

I had originally used [Game Extractor](http://www.watto.org/game_extractor.html) to extract the "ful" and "dbg" files from "img" files, but it's lacking the directory layout.
Hence, I used the [information on the Xentax Wiki](http://wiki.xentax.com/index.php/Futurama_XBox_IMG) to write my own script for "img" extraction.

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
