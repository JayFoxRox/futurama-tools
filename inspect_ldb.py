#!/usr/bin/env python3

import sys
import struct
import os

path = sys.argv[1]

def read8(f):
  return struct.unpack("<B", f.read(1))[0]

def read32(f):
  return struct.unpack("<I", f.read(4))[0]

def read_cstring(f, encoding='latin-1'):
  s = b""
  while True:
    c = f.read(1)
    if c == b'\x00':
      break
    s += c
  return clean_string(s, encoding)

def clean_string(s, encoding):
  z = s.find(b'\x00')
  if z != -1:
    s = s[0:z]
  return s.decode(encoding)

def clean_wide_string(s, encoding):
  z = s.find(b'\x00\x00')
  if z != -1:
    s = s[0:z]
  return s.decode(encoding)

def read_fix_string(f, n=128, encoding='latin-1'):
  s = f.read(n)
  return clean_string(s, encoding)

def read_wide_cstring(f, encoding='utf-16-le'):
  s = b""
  while True:
    c = f.read(2)
    if c == b'\x00\x00':
      break
    s += c
  return clean_wide_string(s, encoding)

with open(path, 'rb') as f:

  magic = read32(f)
  entry_count = read32(f)
  unk2_ptr = read32(f)
  unk3 = read32(f)
  for i in range(15):
    unk1 = read32(f)
    unk2 = read32(f)
    language = read_fix_string(f, n=24)
    print("Found language 0x%08X 0x%08X '%s'" % (unk1, unk2, language))

  assert(f.tell() == unk2_ptr)
  entry_end = unk2_ptr + unk3

  for i in range(entry_count):
    key = read_cstring(f)
    database = read_cstring(f)
    path1 = read_cstring(f)
    path2 = read_cstring(f)
    print("%d. key '%s' in '%s' at '%s', '%s'" % (i, key, database, path1, path2))

  assert(f.tell() == entry_end)

  for i in range(15):
    print("Language %d" % i)
    for j in range(entry_count):
      value = read_wide_cstring(f)
      print("%d. value '%s'" % (j, value))

  cursor = f.tell()
  f.seek(0, os.SEEK_END)
  file_size = f.tell()
  assert(cursor == file_size)
