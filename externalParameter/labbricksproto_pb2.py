# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: labbricksproto.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='labbricksproto.proto',
  package='labbricksproto',
  syntax='proto3',
  serialized_pb=_b('\n\x14labbricksproto.proto\x12\x0elabbricksproto\"8\n\rDeviceRequest\x12\x11\n\tModelName\x18\x01 \x01(\t\x12\x14\n\x0cSerialNumber\x18\x02 \x01(\x03\"L\n\x13\x44\x65viceSetIntRequest\x12\x11\n\tModelName\x18\x01 \x01(\t\x12\x14\n\x0cSerialNumber\x18\x02 \x01(\x03\x12\x0c\n\x04\x44\x61ta\x18\x03 \x01(\x03\"M\n\x14\x44\x65viceSetBoolRequest\x12\x11\n\tModelName\x18\x01 \x01(\t\x12\x14\n\x0cSerialNumber\x18\x02 \x01(\x03\x12\x0c\n\x04\x44\x61ta\x18\x03 \x01(\x08\"o\n\x15\x44\x65viceSetStateRequest\x12\x11\n\tModelName\x18\x01 \x01(\t\x12\x14\n\x0cSerialNumber\x18\x02 \x01(\x03\x12-\n\x05State\x18\x03 \x01(\x0b\x32\x1e.labbricksproto.DeviceStateMsg\"\x94\x01\n\rDeviceInfoMsg\x12\x11\n\tModelName\x18\x01 \x01(\t\x12\x14\n\x0cSerialNumber\x18\x02 \x01(\x03\x12\x0e\n\x06MaxPwr\x18\x03 \x01(\x03\x12\x0e\n\x06MinPwr\x18\x04 \x01(\x03\x12\x0f\n\x07MaxFreq\x18\x05 \x01(\x03\x12\x0f\n\x07MinFreq\x18\x06 \x01(\x03\x12\x18\n\x10HasFastPulseMode\x18\x07 \x01(\x08\"\xfa\x02\n\x0e\x44\x65viceStateMsg\x12\x11\n\tModelName\x18\x10 \x01(\t\x12\x14\n\x0cSerialNumber\x18\x11 \x01(\x03\x12\x11\n\tFrequency\x18\x01 \x01(\x03\x12\x16\n\x0eStartFrequency\x18\x02 \x01(\x03\x12\x14\n\x0c\x45ndFrequency\x18\x03 \x01(\x03\x12\x11\n\tSweepTime\x18\x04 \x01(\x03\x12\x12\n\nPowerLevel\x18\x05 \x01(\x03\x12\x0c\n\x04RFOn\x18\x06 \x01(\x08\x12\x13\n\x0bPulseOnTime\x18\x07 \x01(\x01\x12\x14\n\x0cPulseOffTime\x18\x08 \x01(\x01\x12\x18\n\x10InternalPulseMod\x18\t \x01(\x08\x12\x18\n\x10\x45xternalPulseMod\x18\n \x01(\x08\x12\x13\n\x0bInternalRef\x18\x0b \x01(\x08\x12\x16\n\x0eSweepDirection\x18\x0c \x01(\x08\x12\x11\n\tSweepType\x18\r \x01(\x08\x12\x14\n\x0cPulseRepTime\x18\x0e \x01(\x01\x12\x14\n\x0c\x46\x61stPulsedOn\x18\x0f \x01(\x08\"A\n\x0f\x44\x65viceStateList\x12.\n\x06States\x18\x01 \x03(\x0b\x32\x1e.labbricksproto.DeviceStateMsg2\xac\x05\n\tLabbricks\x12N\n\nDeviceInfo\x12\x1d.labbricksproto.DeviceRequest\x1a\x1d.labbricksproto.DeviceInfoMsg\"\x00\x30\x01\x12P\n\x0b\x44\x65viceState\x12\x1d.labbricksproto.DeviceRequest\x1a\x1e.labbricksproto.DeviceStateMsg\"\x00\x30\x01\x12U\n\x0cSetFrequency\x12#.labbricksproto.DeviceSetIntRequest\x1a\x1e.labbricksproto.DeviceStateMsg\"\x00\x12Q\n\x08SetPower\x12#.labbricksproto.DeviceSetIntRequest\x1a\x1e.labbricksproto.DeviceStateMsg\"\x00\x12Q\n\x07SetRFOn\x12$.labbricksproto.DeviceSetBoolRequest\x1a\x1e.labbricksproto.DeviceStateMsg\"\x00\x12S\n\x08SetState\x12%.labbricksproto.DeviceSetStateRequest\x1a\x1e.labbricksproto.DeviceStateMsg\"\x00\x12Q\n\rUpdateDevices\x12\x1d.labbricksproto.DeviceRequest\x1a\x1d.labbricksproto.DeviceInfoMsg\"\x00\x30\x01\x12X\n\x13\x44\x65viceNotifications\x12\x1d.labbricksproto.DeviceRequest\x1a\x1e.labbricksproto.DeviceStateMsg\"\x00\x30\x01\x62\x06proto3')
)




_DEVICEREQUEST = _descriptor.Descriptor(
  name='DeviceRequest',
  full_name='labbricksproto.DeviceRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ModelName', full_name='labbricksproto.DeviceRequest.ModelName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SerialNumber', full_name='labbricksproto.DeviceRequest.SerialNumber', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=40,
  serialized_end=96,
)


_DEVICESETINTREQUEST = _descriptor.Descriptor(
  name='DeviceSetIntRequest',
  full_name='labbricksproto.DeviceSetIntRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ModelName', full_name='labbricksproto.DeviceSetIntRequest.ModelName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SerialNumber', full_name='labbricksproto.DeviceSetIntRequest.SerialNumber', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='Data', full_name='labbricksproto.DeviceSetIntRequest.Data', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=98,
  serialized_end=174,
)


_DEVICESETBOOLREQUEST = _descriptor.Descriptor(
  name='DeviceSetBoolRequest',
  full_name='labbricksproto.DeviceSetBoolRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ModelName', full_name='labbricksproto.DeviceSetBoolRequest.ModelName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SerialNumber', full_name='labbricksproto.DeviceSetBoolRequest.SerialNumber', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='Data', full_name='labbricksproto.DeviceSetBoolRequest.Data', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=176,
  serialized_end=253,
)


_DEVICESETSTATEREQUEST = _descriptor.Descriptor(
  name='DeviceSetStateRequest',
  full_name='labbricksproto.DeviceSetStateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ModelName', full_name='labbricksproto.DeviceSetStateRequest.ModelName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SerialNumber', full_name='labbricksproto.DeviceSetStateRequest.SerialNumber', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='State', full_name='labbricksproto.DeviceSetStateRequest.State', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=255,
  serialized_end=366,
)


_DEVICEINFOMSG = _descriptor.Descriptor(
  name='DeviceInfoMsg',
  full_name='labbricksproto.DeviceInfoMsg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ModelName', full_name='labbricksproto.DeviceInfoMsg.ModelName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SerialNumber', full_name='labbricksproto.DeviceInfoMsg.SerialNumber', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='MaxPwr', full_name='labbricksproto.DeviceInfoMsg.MaxPwr', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='MinPwr', full_name='labbricksproto.DeviceInfoMsg.MinPwr', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='MaxFreq', full_name='labbricksproto.DeviceInfoMsg.MaxFreq', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='MinFreq', full_name='labbricksproto.DeviceInfoMsg.MinFreq', index=5,
      number=6, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='HasFastPulseMode', full_name='labbricksproto.DeviceInfoMsg.HasFastPulseMode', index=6,
      number=7, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=369,
  serialized_end=517,
)


_DEVICESTATEMSG = _descriptor.Descriptor(
  name='DeviceStateMsg',
  full_name='labbricksproto.DeviceStateMsg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ModelName', full_name='labbricksproto.DeviceStateMsg.ModelName', index=0,
      number=16, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SerialNumber', full_name='labbricksproto.DeviceStateMsg.SerialNumber', index=1,
      number=17, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='Frequency', full_name='labbricksproto.DeviceStateMsg.Frequency', index=2,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='StartFrequency', full_name='labbricksproto.DeviceStateMsg.StartFrequency', index=3,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='EndFrequency', full_name='labbricksproto.DeviceStateMsg.EndFrequency', index=4,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SweepTime', full_name='labbricksproto.DeviceStateMsg.SweepTime', index=5,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='PowerLevel', full_name='labbricksproto.DeviceStateMsg.PowerLevel', index=6,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='RFOn', full_name='labbricksproto.DeviceStateMsg.RFOn', index=7,
      number=6, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='PulseOnTime', full_name='labbricksproto.DeviceStateMsg.PulseOnTime', index=8,
      number=7, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='PulseOffTime', full_name='labbricksproto.DeviceStateMsg.PulseOffTime', index=9,
      number=8, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='InternalPulseMod', full_name='labbricksproto.DeviceStateMsg.InternalPulseMod', index=10,
      number=9, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ExternalPulseMod', full_name='labbricksproto.DeviceStateMsg.ExternalPulseMod', index=11,
      number=10, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='InternalRef', full_name='labbricksproto.DeviceStateMsg.InternalRef', index=12,
      number=11, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SweepDirection', full_name='labbricksproto.DeviceStateMsg.SweepDirection', index=13,
      number=12, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SweepType', full_name='labbricksproto.DeviceStateMsg.SweepType', index=14,
      number=13, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='PulseRepTime', full_name='labbricksproto.DeviceStateMsg.PulseRepTime', index=15,
      number=14, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='FastPulsedOn', full_name='labbricksproto.DeviceStateMsg.FastPulsedOn', index=16,
      number=15, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=520,
  serialized_end=898,
)


_DEVICESTATELIST = _descriptor.Descriptor(
  name='DeviceStateList',
  full_name='labbricksproto.DeviceStateList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='States', full_name='labbricksproto.DeviceStateList.States', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=900,
  serialized_end=965,
)

_DEVICESETSTATEREQUEST.fields_by_name['State'].message_type = _DEVICESTATEMSG
_DEVICESTATELIST.fields_by_name['States'].message_type = _DEVICESTATEMSG
DESCRIPTOR.message_types_by_name['DeviceRequest'] = _DEVICEREQUEST
DESCRIPTOR.message_types_by_name['DeviceSetIntRequest'] = _DEVICESETINTREQUEST
DESCRIPTOR.message_types_by_name['DeviceSetBoolRequest'] = _DEVICESETBOOLREQUEST
DESCRIPTOR.message_types_by_name['DeviceSetStateRequest'] = _DEVICESETSTATEREQUEST
DESCRIPTOR.message_types_by_name['DeviceInfoMsg'] = _DEVICEINFOMSG
DESCRIPTOR.message_types_by_name['DeviceStateMsg'] = _DEVICESTATEMSG
DESCRIPTOR.message_types_by_name['DeviceStateList'] = _DEVICESTATELIST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DeviceRequest = _reflection.GeneratedProtocolMessageType('DeviceRequest', (_message.Message,), dict(
  DESCRIPTOR = _DEVICEREQUEST,
  __module__ = 'labbricksproto_pb2'
  # @@protoc_insertion_point(class_scope:labbricksproto.DeviceRequest)
  ))
_sym_db.RegisterMessage(DeviceRequest)

DeviceSetIntRequest = _reflection.GeneratedProtocolMessageType('DeviceSetIntRequest', (_message.Message,), dict(
  DESCRIPTOR = _DEVICESETINTREQUEST,
  __module__ = 'labbricksproto_pb2'
  # @@protoc_insertion_point(class_scope:labbricksproto.DeviceSetIntRequest)
  ))
_sym_db.RegisterMessage(DeviceSetIntRequest)

DeviceSetBoolRequest = _reflection.GeneratedProtocolMessageType('DeviceSetBoolRequest', (_message.Message,), dict(
  DESCRIPTOR = _DEVICESETBOOLREQUEST,
  __module__ = 'labbricksproto_pb2'
  # @@protoc_insertion_point(class_scope:labbricksproto.DeviceSetBoolRequest)
  ))
_sym_db.RegisterMessage(DeviceSetBoolRequest)

DeviceSetStateRequest = _reflection.GeneratedProtocolMessageType('DeviceSetStateRequest', (_message.Message,), dict(
  DESCRIPTOR = _DEVICESETSTATEREQUEST,
  __module__ = 'labbricksproto_pb2'
  # @@protoc_insertion_point(class_scope:labbricksproto.DeviceSetStateRequest)
  ))
_sym_db.RegisterMessage(DeviceSetStateRequest)

DeviceInfoMsg = _reflection.GeneratedProtocolMessageType('DeviceInfoMsg', (_message.Message,), dict(
  DESCRIPTOR = _DEVICEINFOMSG,
  __module__ = 'labbricksproto_pb2'
  # @@protoc_insertion_point(class_scope:labbricksproto.DeviceInfoMsg)
  ))
_sym_db.RegisterMessage(DeviceInfoMsg)

DeviceStateMsg = _reflection.GeneratedProtocolMessageType('DeviceStateMsg', (_message.Message,), dict(
  DESCRIPTOR = _DEVICESTATEMSG,
  __module__ = 'labbricksproto_pb2'
  # @@protoc_insertion_point(class_scope:labbricksproto.DeviceStateMsg)
  ))
_sym_db.RegisterMessage(DeviceStateMsg)

DeviceStateList = _reflection.GeneratedProtocolMessageType('DeviceStateList', (_message.Message,), dict(
  DESCRIPTOR = _DEVICESTATELIST,
  __module__ = 'labbricksproto_pb2'
  # @@protoc_insertion_point(class_scope:labbricksproto.DeviceStateList)
  ))
_sym_db.RegisterMessage(DeviceStateList)



_LABBRICKS = _descriptor.ServiceDescriptor(
  name='Labbricks',
  full_name='labbricksproto.Labbricks',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=968,
  serialized_end=1652,
  methods=[
  _descriptor.MethodDescriptor(
    name='DeviceInfo',
    full_name='labbricksproto.Labbricks.DeviceInfo',
    index=0,
    containing_service=None,
    input_type=_DEVICEREQUEST,
    output_type=_DEVICEINFOMSG,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DeviceState',
    full_name='labbricksproto.Labbricks.DeviceState',
    index=1,
    containing_service=None,
    input_type=_DEVICEREQUEST,
    output_type=_DEVICESTATEMSG,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='SetFrequency',
    full_name='labbricksproto.Labbricks.SetFrequency',
    index=2,
    containing_service=None,
    input_type=_DEVICESETINTREQUEST,
    output_type=_DEVICESTATEMSG,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='SetPower',
    full_name='labbricksproto.Labbricks.SetPower',
    index=3,
    containing_service=None,
    input_type=_DEVICESETINTREQUEST,
    output_type=_DEVICESTATEMSG,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='SetRFOn',
    full_name='labbricksproto.Labbricks.SetRFOn',
    index=4,
    containing_service=None,
    input_type=_DEVICESETBOOLREQUEST,
    output_type=_DEVICESTATEMSG,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='SetState',
    full_name='labbricksproto.Labbricks.SetState',
    index=5,
    containing_service=None,
    input_type=_DEVICESETSTATEREQUEST,
    output_type=_DEVICESTATEMSG,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateDevices',
    full_name='labbricksproto.Labbricks.UpdateDevices',
    index=6,
    containing_service=None,
    input_type=_DEVICEREQUEST,
    output_type=_DEVICEINFOMSG,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DeviceNotifications',
    full_name='labbricksproto.Labbricks.DeviceNotifications',
    index=7,
    containing_service=None,
    input_type=_DEVICEREQUEST,
    output_type=_DEVICESTATEMSG,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_LABBRICKS)

DESCRIPTOR.services_by_name['Labbricks'] = _LABBRICKS

# @@protoc_insertion_point(module_scope)
