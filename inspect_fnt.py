#!/usr/bin/env python3

import sys
import struct

def read8(f):
  return struct.unpack("<B", f.read(1))[0]

def read16(f):
  return struct.unpack("<H", f.read(2))[0]

def read16s(f):
  return struct.unpack("<h", f.read(2))[0]

def read32(f):
  return struct.unpack("<I", f.read(4))[0]

for path in sys.argv[1:]:

  with open(path, "rb") as f:

    print("Parsing '%s'" % path)

    width = read16(f)
    height = read16(f)
    unk1 = read16(f)
    unk2 = read16(f) # Number of row changes?
    row_height = read16(f)
    
    print("Texture: (%d, %d); unknown: %d,%d, row-height: %d" % (width, height, unk1, unk2, row_height))

    assumed_x_padding = None
    expected_x = None
    expected_y = height - row_height
    expected_h = row_height

    for i in range(256):
      
      # Read a glyph
      glyph = read16s(f)
      assert(glyph == 0 or glyph == i)
      x = read16s(f)
      y = read16s(f)
      w = read16s(f)
      h = read16s(f)

      # Print information
      printable_glyph = ''
      if i < 32 or i >= 127:
        printable_glyph = ""
      else:
        printable_glyph = ", symbol: '%c'" % i
      print("%3d. glyph: %3d, position: (%4d,%4d), size: (%2d,%2d)%s" % (i, glyph, x, y, w, h, printable_glyph))

      if True:

        # Use x coordinate of first glyph as padding assumption
        if assumed_x_padding == None:
          assumed_x_padding = x
          expected_x = assumed_x_padding

        # Test assumption about row height
        assert(h == expected_h)

        # Get padded size for assumption about coordinates
        padded_w = assumed_x_padding + w + assumed_x_padding
        padded_h = h

        # If we reached the border of the image, go to next row
        if x < expected_x:
          expected_y -= padded_h
          expected_x = assumed_x_padding
        assert(x == expected_x)
        assert(y == expected_y)

        # Advance cursor
        expected_x += padded_w


    #FIXME: Assert that f.tell() is file_size
