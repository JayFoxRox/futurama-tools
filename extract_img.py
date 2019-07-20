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
  root_directory_end = f.tell() + root_directory_size - 7
  print("Root directory is %d bytes" % root_directory_size)
  print(root_directory_end)

  path = []
  while f.tell() < root_directory_end:

    print()
    print(f.tell())
    print(path)

    entry_name = parse_string(f)
    align(f, 4)

    is_folder = entry_name[0] & 0x80
    if is_folder:
      entry_name = bytes([entry_name[0] ^ 0x80]) + entry_name[1:]
    entry_name = entry_name.decode('ascii')

    usable_path = [x[0] for x in path]
    system_path = os.path.join(base_path, *usable_path, entry_name)

    if is_folder:
      # Read a directory
      directory_size = read32(f)
      print("Directory %d" % directory_size)
      try:
        os.mkdir(system_path)
      except FileExistsError:
        pass
      path += [(entry_name, f.tell() + directory_size - 4)]
    else:
      # Read a file
      file_size = read32(f)
      file_offset = read32(f)
      print("File (at %d, %d bytes) in '%s'" % (file_offset, file_size, "/".join(usable_path)))
      extract_file(f, file_offset, file_size, system_path)
    print(entry_name)

    while len(path) > 0 and f.tell() >= path[-1][1]:
      directory_end = path.pop(-1)[1]
      assert(f.tell() == directory_end)

  assert(f.tell() == root_directory_end)
