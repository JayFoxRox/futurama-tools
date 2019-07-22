#!/usr/bin/env python3

import struct
import sys
import os
import time
import pprint

HEADER_LENGTH = 40

def read32(f):
  return struct.unpack("<I", f.read(4))[0]

def read_string(f):
  l = read32(f)
  assert(l % 4 == 0)
  return f.read(l)

def extract_file(f, offset, size, path):
  cursor = f.tell()
  f.seek(offset)
  with open(path, "wb") as fo:
    while size > 0:
      chunk_size = min(size, 1 * 1024 * 1024)
      data = f.read(chunk_size)
      fo.write(data)
      size -= len(data)
  f.seek(cursor)

file_path = sys.argv[1]
base_path = sys.argv[2]

with open(file_path, "rb") as f:

  def parse_string(f):
    s = b""
    while True:
      c = f.read(1)
      if c == b"\x00":
        break
      s += c
    return s

  def align(f, alignment):
    while f.tell() % alignment != 0:
      f.read(1)

  root_directory_size = read32(f)

  # The lower 3 bits might reveal platform?
  platform = root_directory_size & 3
  root_directory_size = root_directory_size & ~3

  # Output platform info
  if platform == 0:
    print("Assuming platform: PlayStation 2")
  elif platform == 3:
    print("Assuming platform: Original Xbox")
  else:
    print("Unknown platform %d" % platform)

  # Separate mainloop from header
  print()

  # Tell user what size this is
  #FIXME: This could re-use code that also exists below
  root_directory_end = f.tell() + root_directory_size - 4
  print("/: Directory (size %d)" % root_directory_size)

  # Loop over all entries
  path = []
  while f.tell() < root_directory_end:

    #print()
    #print(f.tell())
    #print(path)

    entry_name = parse_string(f)
    assert(len(entry_name) > 0)
    align(f, 4)

    is_folder = entry_name[0] & 0x80
    if is_folder:
      entry_name = bytes([entry_name[0] ^ 0x80]) + entry_name[1:]
    entry_name = entry_name.decode('ascii')

    # Construct relative path within image
    entry_directory_list = [x[0] for x in path]
    entry_path = "/".join(entry_directory_list + [entry_name])

    # Create a path for he host file system
    system_path = os.path.join(base_path, *entry_directory_list, entry_name)

    # Read entry size
    entry_size = read32(f)

    if is_folder:
      # Read a directory
      assert(entry_size % 4 == 0)
      print("/%s: Directory (size %d)" % (entry_path, entry_size))
      try:
        os.mkdir(system_path)
      except FileExistsError:
        pass
      path += [(entry_name, f.tell() + entry_size - 4)]
    else:
      # Read a file
      data_offset = read32(f)
      assert(data_offset % 2048 == 0)
      print("/%s: File (size %d, offset %d)" % (entry_path, entry_size, data_offset))
      extract_file(f, data_offset, entry_size, system_path)
    #print(entry_name)

    while len(path) > 0 and f.tell() >= path[-1][1]:
      directory_end = path.pop(-1)[1]
      assert(f.tell() == directory_end)

  # Inform user
  print()
  print("Extraction complete")

  assert(root_directory_end == f.tell())
