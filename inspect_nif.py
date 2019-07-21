#!/usr/bin/env python3

import sys
import logging

logging.basicConfig(level=logging.DEBUG)

from pyffi.formats.nif import NifFormat

for path in sys.argv[1:]:

  stream = open(path, 'rb')
  data = NifFormat.Data()
  data.inspect(stream) # the file seems ok on inspection
  data.read(stream) # doctest: +ELLIPSIS

  print(data.version)

  stream.close()
