#!/usr/bin/env python3

import struct
import sys
import os
import time
import pprint

HEADER_LENGTH = 40

def read8(f):
  return struct.unpack("<B", f.read(1))[0]

def read32(f):
  return struct.unpack("<I", f.read(4))[0]

def read32s(f):
  return struct.unpack("<i", f.read(4))[0]

def read_string(f):
  l = read32(f)
  assert(l % 4 == 0)
  return f.read(l)

def clean_string(s):
  z = s.find(b'\x00')
  if z != -1:
    s = s[0:z]
  return s.decode('latin-1')

def read_fix_string(f, n=128):
  s = f.read(n)
  return clean_string(s)

def read_operation(f):
  
  operation_information = {}

  operation_information['address'] = f.tell() - HEADER_LENGTH

  unk1 = read8(f)
  operation_information['unk1'] = unk1 # Something to do with branching?
  unk2 = read8(f)
  operation_information['unk2'] = unk2 # Source line?
  #print(unk1)
  #assert((unk1 == 0x00) or (unk1 == 0x01))
  #print(unk2)
  #assert((unk2 == 0x27) or (unk2 == 0x25))
  unk3 = read8(f)
  operation_information['unk3'] = unk3 # Source file?
  operation_type = read8(f)
  operation_information['type'] = operation_type

  # Helper, as I'm trying to make out a pattern..
  if unk1 == 0:
    pass
  elif unk1 == 1:
    #print("ONE: %d" % operation_type)
    assert((operation_type == 4) or (operation_type == 5) or (operation_type == 6) or (operation_type == 10) or (operation_type == 11) or (operation_type == 12))
  elif unk1 == 2:
    #print("TWO: %d" % operation_type)
    assert((operation_type == 5) or (operation_type == 6) or (operation_type == 11))
  else:
    print()
    print(unk1)
    assert(False)  
  

  if operation_type == 2:
    value = []
  elif operation_type == 3:
    value = []
  elif operation_type == 4:
    a = read32(f)
    assert(a % 4 == 0)
    b = read32(f)
    assert(b % 4 == 0)
    value = [a, b]
  elif operation_type == 5:
    address = read32(f)
    value = [address]
  elif operation_type == 6:
    offset = read32(f)
    value = [offset]
  elif operation_type == 8:
    value = read32(f) # Used for floats and integers?
  elif operation_type == 9:
    value = read_string(f)
  elif operation_type == 10:
    a = read32(f)
    assert(a % 4 == 0)
    b = read32(f)
    assert(b % 4 == 0)
    value = [a, b]
  elif operation_type == 11:
    address = read32(f)
    value = [address]
  elif operation_type == 12:
    # Only occurs once (at least in level1-1)
    a = read32(f)
    b = read32(f)
    value = [a, b]
  elif operation_type == 14:
    unk1 = read32(f)
    assert(unk1 == 4)
    value = [unk1]
  elif operation_type == 15:
    offset = read32s(f)
    value = [offset]
  elif operation_type == 16:
    offset = read32s(f)
    value = [offset]
  elif operation_type == 17:
    offset = read32s(f)
    value = [offset]
  elif operation_type == 18:
    offset = read32s(f)
    b = read32s(f) # Stack size?
    assert(b % 4 == 0)
    value = [offset, b]
  elif operation_type == 19:
    class_index = read32(f) # Class
    function_index = read32(f) # Function index
    value = [class_index, function_index]
  elif operation_type == 20:
    offset = read32s(f)

    a = read32(f) # ???
    assert(a % 4 == 0)
    b = read32(f) # ???
    assert(b % 4 == 0)

    value = [offset, a, b]
  elif operation_type == 21:
    value = []
  elif operation_type == 22:
    value = []
  elif operation_type == 23:
    value = []
  elif operation_type == 24:
    value = []
  elif operation_type == 25:
    value = []
  elif operation_type == 26:
    unk1 = read32(f)
    value = [unk1]
  elif operation_type == 27:
    unk1 = read32(f)
    assert(unk1 % 4 == 0)
    unk2 = read32(f)
    assert(unk2 % 4 == 0)
    value = [unk1, unk2]
  else:
    print("Unknown type %d" % operation_type)
    sys.exit(1)

  operation_information['value'] = value

  return operation_information

def read_symbol(f):
  symbol = {}

  name = read_fix_string(f)
  symbol['name'] = name
  offset = read32(f)
  symbol['offset'] = offset
  type_id = read32(f)
  symbol['type'] = type_id

  return symbol

def read_function(f):

  function_information = {}

  next_function = read32(f)
  name = read_fix_string(f)
  function_information['name'] = name
  path = read_fix_string(f)
  function_information['path'] = path
  address = read32(f)
  function_information['address'] = address
  unk2 = read32(f) # Class type probably
  function_information['type'] = unk2
  function_index = read32(f)
  unk4 = read32(f)
  function_information['unk4'] = unk4
  local_count = read32(f)
  local_list = read32(f)
  #assert((unk2 == 0) or (unk2 == 0x29))

  locals = []
  f.seek(local_list)
  for j in range(local_count):
    locals += [read_symbol(f)]
  function_information['locals'] = locals

  #print(function_information)
  assert((unk4 == 1) or (unk4 == 2) or (unk4 == 17) or (unk4 == 33) or (unk4 == 129) or (unk4 == 385))

  return next_function, (unk2, function_index), function_information

def read_type(f):

  type_information = {}

  next_type = read32(f)
  name = read_fix_string(f)
  type_information['name'] = name
  type_index = read32(f)
  member_count = read32(f)
  member_list = read32(f)
  #print("-- next:%d index:%d memberCount:%d memberList:%d / '%s'" % (next_type, type_index, member_count, member_list, name))

  members = []
  f.seek(member_list)
  for j in range(member_count):
    members += [read_symbol(f)]
  type_information['members'] = members
  
  return next_type, type_index, type_information

def read_debug_symbols(f):

  debug_symbols = {}

  unk1 = read32(f)
  assert(unk1 == 8)
  function_list = read32(f)
  type_list = read32(f) # Points to this field in next chunk 
  name = read_fix_string(f)
  debug_symbols['name'] = name
  unk4 = read32(f)
  assert(unk4 == 0)
  member_count = read32(f)
  member_list = read32(f)
  #print("memberCount:%d memberList:%d; unk1:0x%08X function_list:%d type_list:%d unk4:%d; library '%s'" % (member_count, member_list, unk1, function_list, type_list, unk4, name))

  variables = []
  f.seek(member_list)
  for j in range(member_count):
    #print("index %d at %d" % (j, f.tell()))
    variables += [read_symbol(f)]
  debug_symbols['variables'] = variables

  functions = {}
  f.seek(function_list)
  j = 0
  while True:
    #print("index %d at %d" % (j, f.tell()))
    next_function, function_index, function_information = read_function(f)
    assert(not function_index in functions)
    functions[function_index] = function_information
    if next_function == 0:
      break
    f.seek(next_function)
    j += 1
  debug_symbols['functions'] = functions

  types = {}
  f.seek(type_list)
  j = 0
  while True:
    #print("index %d at %d" % (j, f.tell()))
    next_type, type_index, type_information = read_type(f)
    assert(not type_index in types)
    types[type_index] = type_information
    if next_type == 0:
      break
    f.seek(next_type)
    j += 1
  debug_symbols['types'] = types

  return debug_symbols

script_path = sys.argv[1]
debug_path = sys.argv[2]

#FIXME: Create dummy / empty debug symbols in memory

print("# Futurama Script disassembler")

#FIXME: Should be optional
with open(debug_path, "rb") as f:
  debug_symbols = read_debug_symbols(f)
  #pprint.pprint(debug_symbols)
  print("# Loaded debug symbols '%s' (Target script: '%s')" % (debug_path, debug_symbols['name']))

if True:
  for t in sorted(debug_symbols['types']):
    print("# %d: %s" % (t, str(debug_symbols['types'][t])))

if True:
  for v in debug_symbols['variables']:
    print("# var: %s" % str(v))

if True:
  for t in debug_symbols['functions']:
    function = debug_symbols['functions'][t]
    print("# %s: %s" % (str(t), str(function)))

with open(script_path, "rb") as f:

  print("# Loaded script '%s'" % script_path)
  print("# ")      

  # File repeats after half, but with flipped endianess; get second magic
  f.seek(0, os.SEEK_END)
  file_length = f.tell() // 2
  f.seek(file_length)
  swapped_magic = f.read(4)

  # Go back to start; and check magic
  f.seek(0)
  magic = f.read(4)
  assert(magic == swapped_magic[::-1])

  # Continue reading the header
  #FIXME: What's in there?
  assert(HEADER_LENGTH % 4 == 0)
  for i in range((HEADER_LENGTH - 4) // 4):

    comments = {
      12: "Variable space size",
      32: "ExitPoint address"
    }

    cursor = f.tell()
    value = read32(f)
    if cursor in comments:
      comment = "; " + comments[cursor]
    else:
      comment = ""
    print(".raw 0x%08X # header at offset %d%s" % (value, cursor, comment))

  # Split header and code
  print()

  def find_functions_by_address(address):
    functions = []
    for key in debug_symbols['functions']:
      function = debug_symbols['functions'][key]

      #FIXME: What does this mean? 
      if function['unk4'] == 2:
        assert(function['address'] == 0)
      else:

        if function['address'] == address:
          functions += [function]
    return functions

  def find_variable_by_address(address):
    variables = []
    #FIXME: This assumes the variables are sorted by address
    for variable in debug_symbols['variables'][::-1]:
      offset = address - variable['offset']
      if offset >= 0:
        variables += [(variable, offset)]
    return variables
  
  def find_type_member_by_offset(type_index, offset):
    if type_index == 0:
      members = debug_symbols['variables']
    else:
      type_information = debug_symbols['types'][type_index]
      members = type_information['members']
    if len(members) == 0:
      if offset == 0:
        return True
      return False
    #FIXME: This assumes the members are sorted by offset
    for member in members[::-1]:
      if offset >= member['offset']:
        return member #FIXME: Handle case where multiple fields share the same offset
    return None

  def find_type_member_path(type_index, offset, field=True):
    def search(path, type_index, offset):

      # Skip the fields
      if not field:
        if offset == 0:
          return path

      member = find_type_member_by_offset(type_index, offset)

      # Still at an offset, and no more childs exist
      if member == False:
        return False

      # Found exact member, and no more childs exist
      if member == True:
        return path

      path += [member]

      # No matching member found
      if member == None:
        assert(False)
        return path

      type_index = member['type']
      offset = offset - member['offset']
      #if offset != 0:
      return search(path, type_index, offset)
      #else:
      #  #FIXME: Keep searching until there's no more sub-members?
      #  return path

    #FIXME: Do most of this in callee?
    path = search([], type_index, offset)
    if path == False:
      return None

    # Alternative to field check above: Only remove final element
    if False:
      if not field:
        path = path[:-1]

    path = [x['name'] if x != None else "???" for x in path]
    return ".".join(path)

  def find_variable_member_path(address, field=True):
    variables = find_variable_by_address(address)
    if len(variables) == 0:
      return "variable_%d" % address

    #FIXME: It appears, that there's also re-use of memory
    #assert(len(variables) == 1)
    members = []
    for variable in variables:
      path = find_type_member_path(variable[0]['type'], variable[1], field)
      if path != None:
        #FIXME: Keep path as list, and use proper string join
        if len(path) == 0:
          members += [variable[0]['name']]
        else:
          members += ["%s.%s" % (variable[0]['name'], path)]

    return members

  def find_variables_member_path(variables, offset, field=True):
    local = []
    #FIXME: This assumes the locals are sorted by offset
    for l in variables[::-1]:
      if offset >= l['offset']:
        member_path = find_type_member_path(l['type'], offset - l['offset'], field) 
        if member_path != None and len(member_path) > 0:
          local += ["%s.%s" % (l['name'], member_path)]
        else:
          local += [l['name']]
        break
    return local

  def find_local_member_path(functions, offset, field=True):
    result = []
    for function in functions:
      result += find_variables_member_path(function['locals'], offset, field)
    return result

  functions = []
  known_line = None
  def decode_operation(f):
    global functions
    global known_line


    def find_function_member_path(offset, field=True):
      if len(functions) != 1:
        return None

      function = functions[0]
      if function['type'] == 0:
        variables = debug_symbols['variables']
        function_type_name = ""
      else:
        function_type = debug_symbols['types'][function['type']]
        variables = function_type['members']
        function_type_name = function_type['name']

      path = find_variables_member_path(variables, offset, field)

      return "%s!%s" % (function_type_name, ".".join(path))
       

    cursor = f.tell() - HEADER_LENGTH
      
    operation = read_operation(f)
    #print(operation)

    #FIXME: Also respect the source module?
    # Try to add line breaks, whenever the source line changed
    line = (operation['unk2'], operation['unk3'])
    if known_line != line:
      if known_line != None:
        print()
      known_line = line
      print(".line %d %d # source line / module?" % (operation['unk2'], operation['unk3']))

    print(":label_%d # (0x%X)" % (cursor, cursor))

    def to_float(i):
      return struct.unpack("<f", struct.pack("<I", i))[0]

    def find_function_by_address(address):
      functions = find_functions_by_address(address)
      assert(len(functions) == 1)
      return functions[0]

    def get_function_comment(function):
      if function['type'] != 0:
        function_type_name = debug_symbols['types'][function['type']]['name']
      else:
        function_type_name = ""
      return "%s!%s" % (function_type_name, function['name'])

    def get_label(address):

      # Ensure target exists
      if True:
        off = f.tell()
        f.seek(HEADER_LENGTH + address)
        operation = read_operation(f)
        #print(operation)
        f.seek(off)

      return "label_%d" % address

    def find_type_members_by_offset(offset):
      members = []
      for type_index in debug_symbols['types']:
        member = get_type_member_string(type_index, offset)
        if member != None:
          members += [member]
      return members


    operation_address = operation['address']
    operation_type = operation['type']
    operation_value = operation['value']
    if operation_type == 2:
      if operation['unk1'] == 0:
        # This function seems to set condition flags / produces conditions
        # It checks wether the time from he 
        print("CHECK_COUNTDOWN_2.0")
      else:
        assert(False)
    elif operation_type == 3:
      if operation['unk1'] == 0:
        # Takes one float value
        # It seems to return immediately, but starts measuring time
        print("SET_COUNTDOWN_3.0")
      else:
        assert(False)
    elif operation_type == 4:

      # Push "object.field" (object with field) ?

      if operation['unk1'] == 0:
        print("PUSH local-field %d size %d # %s" % (operation_value[0], operation_value[1], find_local_member_path(functions, operation_value[0])))
      elif operation['unk1'] == 1:
        print("PUSH class-field %d size %d # %s" % (operation_value[0], operation_value[1], find_function_member_path(operation_value[0])))
      else:
        assert(False)
    elif operation_type == 5:

      # Push "object" (object without field) ?

      if operation['unk1'] == 0:
        print("PUSH local %d # %s" % (operation_value[0], find_local_member_path(functions, operation_value[0], False)))
      elif operation['unk1'] == 1:
        print("PUSH_5 class %d # %s" % (operation_value[0], find_function_member_path(operation_value[0], False)))
      elif operation['unk1'] == 2:
        print("PUSH global %d # %s" % (operation_value[0], find_variable_member_path(operation_value[0], False)))
      else:
        assert(False)
    elif operation_type == 6:

      # Push "object" (object without field) ?

      # This seems to pass by reference?!
      if operation['unk1'] == 0:
        print("PUSH &local %d # %s" % (operation_value[0], find_local_member_path(functions, operation_value[0], False)))
      elif operation['unk1'] == 1: 
        print("PUSH &class %d # %s" % (operation_value[0], find_function_member_path(operation_value[0], False)))
      elif operation['unk1'] == 2:
        print("PUSH &global %d # %s" % (operation_value[0], find_variable_member_path(operation_value[0], False)))
      else:
        assert(False)
    elif operation_type == 8:
      # Confirmed
      if operation['unk1'] == 0:

        def probablyFloat(bits):
          sign = (bits & 0x80000000) != 0;
          exp = ((bits & 0x7F800000) >> 23) - 127;
          mant =  bits & 0x007FFFFF;

          # +-0 should be integer
          if (exp == -127 and mant == 0):
            return False

          # -1 billionth to +1 billion
          if (-30 <= exp and exp <= 30):
            return True

          # Value with only a few binary digits is float
          if ((mant & 0x0000FFFF) == 0):
            return True

          return False

        #FIXME: Peek at the next operation. If it's YIELD, then we want float

        float_value = to_float(operation_value)
        if probablyFloat(operation_value):    
          #FIXME: Remove trailing zeros
          #FIXME: Ensure our reacked float is still an exact integer match    
          print("PUSH float %f # integer: 0x%08X" % (float_value, operation_value))
        else:
          print("PUSH integer %d # float: %f" % (operation_value, float_value))
      else:
        assert(False)
    elif operation_type == 9:
      # Confirmed
      if operation['unk1'] == 0:
        print("PUSH string \"%s\"" % clean_string(operation_value).encode('unicode_escape').decode('utf-8').replace("\"", "\\\""))
      else:
        assert(False)
    elif operation_type == 10:

      # Pop "object.field" (object with field)

      #FIXME: Only used to pop function results?

      if operation['unk1'] == 0:
        print("POP local-offset %d size %d # %s" % (operation_value[0], operation_value[1], find_local_member_path(functions, operation_value[0])))
      elif operation['unk1'] == 1:
        print("POP class-offset %d size %d # %s" % (operation_value[0], operation_value[1], find_function_member_path(operation_value[0])))
      else:
        assert(False)
    elif operation_type == 11:

      # Pop "object" (object without field)

      #FIXME: Unsure
      if operation['unk1'] == 0:
        print("POP_11.0 local %d # %s" % (operation_value[0], find_local_member_path(functions, operation_value[0], False)))
      elif operation['unk1'] == 1:
        print("POP_11.1 class %d # %s" % (operation_value[0], find_function_member_path(operation_value[0], False)))
      elif operation['unk1'] == 2:
        print("POP_11.2 global %d # %s" % (operation_value[0], find_variable_member_path(operation_value[0], False)))
      else:
        assert(False)
    elif operation_type == 12:

      # Pop "object" (object without field)

      # Used in interesting patter like this:
      #UNKNOWN_MOVE_STACK_12.0 offset 20 size 4 # ['i5']
      #UNKNOWN_MOVE_STACK_12.0 offset 16 size 4 # ['i4']
      #UNKNOWN_MOVE_STACK_12.0 offset 12 size 4 # ['i3']
      #UNKNOWN_MOVE_STACK_12.0 offset 8 size 4 # ['i2']
      #POP_TO_STACK_11.0 offset 4 # ['i1']

      #FIXME: Very unsure
      if operation['unk1'] == 0:
        print("POP local-offset %d size %d # %s" % (operation_value[0], operation_value[1], find_local_member_path(functions, operation_value[0])))
      elif operation['unk1'] == 1:
        print("POP class-offset %d size %d # %s" % (operation_value[0], operation_value[1], find_function_member_path(operation_value[0])))
      else:
        assert(False)
    elif operation_type == 14:
      if operation['unk1'] == 0:
        # Probably removes X bytes from stack?
        # Argument is always 4 (at least in level1-1)
        print("DISCARD size %d" % (operation_value[0]))
      else:
        assert(False)
    elif operation_type == 15:
      if operation['unk1'] == 0:
        print("GOTO label %s" % get_label(operation_address + operation_value[0] + 8))
    elif operation_type == 16:
      if operation['unk1'] == 0:
        # Might be another condition?
        print("GOTO_IF_FALSE label %s" % get_label(operation_address + operation_value[0] + 8))
      else:
        assert(False)
    elif operation_type == 17:
      if operation['unk1'] == 0:
        # Might be another condition?
        print("GOTO_IF_TRUE label %s" % get_label(operation_address + operation_value[0] + 8))
      else:
        assert(False)
    elif operation_type == 18:
      target = operation_address + operation_value[0] + 12
      target_function = find_function_by_address(target)
      if operation['unk1'] == 0:
        print("CALL_18 label %s stack_size %d # %s" % (get_label(target), operation_value[1], get_function_comment(target_function)))
      else:
        assert(False)

      # Always seems to reference operation 27?!
      if True:
        off = f.tell()
        f.seek(HEADER_LENGTH + target)
        operation = read_operation(f)
        #print(operation['type'])
        # WTF?!
        if operation['unk2'] == 0:
          assert((operation['type'] == 5) or (operation['type'] == 6) or (operation['type'] == 22) or (operation['type'] == 27))
        else:
          assert(operation['type'] == 27)
        f.seek(off)


    elif operation_type == 19:
      # Confirmed

      if operation['unk1'] == 0:
        class_index = operation_value[0]
        function_index = operation_value[1]
        function = debug_symbols['functions'][(class_index, function_index)]
        comment = get_function_comment(function)

        print("CALL class %d function %d # %s" % (class_index, function_index, comment))
      else:
        assert(False)

    elif operation_type == 20:
      target = operation_address + operation_value[0] + 16
      target_function = find_function_by_address(target)
      if operation['unk1'] == 0:

        if False:
          print()
          for y in debug_symbols['types']:
            print(y)
            x = find_type_member_path(y, operation_value[2])
            print("--- type %s: %s" % (debug_symbols['types'][y]['name'], x))

        print("CALL_20.0 label %s stack_size %d unknown %d # %s" % (get_label(target), operation_value[1], operation_value[2], get_function_comment(target_function)))
      else:
        assert(False)

      # Always seems to reference operation 27?!
      if True:
        off = f.tell()
        f.seek(HEADER_LENGTH + target)
        operation = read_operation(f)
        #print(operation['type'])
        assert(operation['type'] == 27)
        f.seek(off)

    elif operation_type == 21:
      if operation['unk1'] == 0:
        # Always follows one of these:
        # - PUSH_FROM_VARIABLE_5.1 address 0 # Often: @@AID@@ for all types
        # - PUSH_FROM_VARIABLE_5.1 address 92 # Rarely: @@AID@@ for global type
        print("UNKNOWN_LOCK_AID_21.0")
      else:
        assert(False)

    elif operation_type == 22:
      if operation['unk1'] == 0:
        print("CREATE_OBJECT_22.0")
      else:
        assert(False)

    elif operation_type == 23:
      if operation['unk1'] == 0:
        print("DESTROY_OBJECT_23.0")
      else:
        assert(False)

    elif operation_type == 24:
      if operation['unk1'] == 0:
        # Takes a float argument on stack
        print("YIELD")
      else:
        assert(False)

    elif operation_type == 25:
      if operation['unk1'] == 0:
        #FIXME: Not sure what this does, "UNLOCK" is a theory
        print("END_FUNCTION_UNLOCK_25.0")
        print("")
        functions = []
      else:
        assert(False)


    elif operation_type == 26:
      if operation['unk1'] == 0:
        print("END_FUNCTION_26.0 stack_size %d" % (operation_value[0]))
        print("")
        functions = []
      else:
        assert(False)

    elif operation_type == 27:

      if operation['unk1'] == 0:

        print("")

        functions = find_functions_by_address(cursor)
        if len(functions) > 0:
          assert(len(functions) == 1)
          print("# LABEL: %s" % str(functions))

        print("BEGIN_FUNCTION stack_size %d extra_stack_size %d" % (operation_value[0], operation_value[1]))

        # Dump table of locals
        if len(functions) == 1:
          function = functions[0]
          function_type = function['type']
          if function_type != 0:
            print(".class %s" % debug_symbols['types'][function_type]['name'])
          local = function['locals']
          if len(local) > 0:
            #FIXME: Add empty line here?
            for l in local:
              #FIXME: Add dummy locals for alignment if necessary
              type_name = debug_symbols['types'][l['type']]['name']
              print(".local %s %s # Offset %d" % (type_name, l['name'], l['offset']))

      else:
        assert(False)

    else:
      print("UNKNOWN_%d.%d %s" % (operation_type, operation['unk1'], str(operation_value)))
      assert(False)

  if False:
    f.seek(432)
    decode_operation(f)

    f.seek(0x330)
    decode_operation(f)

    f.seek(0x700)
    decode_operation(f)

    f.seek(0x9CC)
    decode_operation(f)

    f.seek(0xD80)
    decode_operation(f)

    f.seek(0x23E0)
    decode_operation(f)

    f.seek(0x2428)
    decode_operation(f)

    f.seek(0x2464)
    decode_operation(f)

    f.seek(0xB104)
    decode_operation(f)

    f.seek(0x1064C)
    decode_operation(f)

    f.seek(0x113F0)
    decode_operation(f)

    f.seek(0x114B8)
    decode_operation(f)

    f.seek(0x11664)
    decode_operation(f)

    print("@@action@@aDoorInnerZoid")
    f.seek(26196)
    f.read(4)
    decode_operation(f)

  if False:
    print(find_type_member_path(8, 0))
    sys.exit(0)

  if False:
    for x in find_variable_by_address(540):
      print(x)
    print()
    for x in find_variable_member_path(540):
      print(x)
    sys.exit(0)

  while f.tell() < file_length:
    #FIXME: add line breaks if there's a change in source-line numbers
    decode_operation(f)
    


