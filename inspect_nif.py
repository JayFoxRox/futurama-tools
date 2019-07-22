#!/usr/bin/env python3

import sys
import logging
import os

logging.basicConfig(level=logging.DEBUG)

from pyffi.formats.nif import NifFormat

for path in sys.argv[1:]:

  stream = open(path, 'rb')
  data = NifFormat.Data()
  data.inspect(stream) # the file seems ok on inspection
  data.read(stream) # doctest: +ELLIPSIS

  print("nif version 0x%08X, user version %d" % (data.version, data.user_version))

  for root in data.roots:
    for block in root.tree():
      if isinstance(block, NifFormat.NiNode):
        #print(block)
        print(block.name.decode("ascii"))
        for block in block.tree():
          if isinstance(block, NifFormat.NiUDSFileObject):
            name = block.name.decode("ascii")
            print("Found file '%s'" % name)
            #print(block)

            path = name.split("\\")
      
            if True:

              # Construct a final folder and construct it
              system_path = os.path.join("out", *path)
              os.makedirs(os.path.dirname(system_path), exist_ok=True)

              # Create usable path to file, and write it
              with open(system_path, "wb") as f:
                f.write(bytes([x for x in block.data]))

  stream.close()
