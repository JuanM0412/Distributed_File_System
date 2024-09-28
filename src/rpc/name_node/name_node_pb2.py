# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: name_node.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'name_node.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fname_node.proto\x12\x08nameNode\"@\n\x0fRegisterRequest\x12\n\n\x02ip\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\t\x12\x13\n\x0b\x63\x61pacity_MB\x18\x03 \x01(\x01\"\x1e\n\x10RegisterResponse\x12\n\n\x02id\x18\x01 \x01(\t\"F\n\x16\x44\x61taNodesUploadRequest\x12\x0c\n\x04\x66ile\x18\x01 \x01(\t\x12\x0c\n\x04size\x18\x02 \x01(\x01\x12\x10\n\x08username\x18\x03 \x01(\t\"L\n\x11\x44\x61taNodesResponse\x12%\n\x05nodes\x18\x01 \x03(\x0b\x32\x16.nameNode.DataNodeInfo\x12\x10\n\x08\x62lock_id\x18\x02 \x01(\t\"I\n\x0c\x44\x61taNodeInfo\x12\n\n\x02id\x18\x01 \x01(\t\x12\n\n\x02ip\x18\x02 \x01(\t\x12\x0c\n\x04port\x18\x03 \x01(\t\x12\x13\n\x0b\x63\x61pacity_MB\x18\x04 \x01(\x01\"4\n\x0e\x41\x64\x64UserRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"!\n\x0f\x41\x64\x64UserResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\"9\n\x13ValidateUserRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"&\n\x14ValidateUserResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\":\n\x18\x44\x61taNodesDownloadRequest\x12\x0c\n\x04\x66ile\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t2\x97\x03\n\x0fNameNodeService\x12\x41\n\x08Register\x12\x19.nameNode.RegisterRequest\x1a\x1a.nameNode.RegisterResponse\x12V\n\x15GetDataNodesForUpload\x12 .nameNode.DataNodesUploadRequest\x1a\x1b.nameNode.DataNodesResponse\x12Z\n\x17GetDataNodesForDownload\x12\".nameNode.DataNodesDownloadRequest\x1a\x1b.nameNode.DataNodesResponse\x12>\n\x07\x41\x64\x64User\x12\x18.nameNode.AddUserRequest\x1a\x19.nameNode.AddUserResponse\x12M\n\x0cValidateUser\x12\x1d.nameNode.ValidateUserRequest\x1a\x1e.nameNode.ValidateUserResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'name_node_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_REGISTERREQUEST']._serialized_start=29
  _globals['_REGISTERREQUEST']._serialized_end=93
  _globals['_REGISTERRESPONSE']._serialized_start=95
  _globals['_REGISTERRESPONSE']._serialized_end=125
  _globals['_DATANODESUPLOADREQUEST']._serialized_start=127
  _globals['_DATANODESUPLOADREQUEST']._serialized_end=197
  _globals['_DATANODESRESPONSE']._serialized_start=199
  _globals['_DATANODESRESPONSE']._serialized_end=275
  _globals['_DATANODEINFO']._serialized_start=277
  _globals['_DATANODEINFO']._serialized_end=350
  _globals['_ADDUSERREQUEST']._serialized_start=352
  _globals['_ADDUSERREQUEST']._serialized_end=404
  _globals['_ADDUSERRESPONSE']._serialized_start=406
  _globals['_ADDUSERRESPONSE']._serialized_end=439
  _globals['_VALIDATEUSERREQUEST']._serialized_start=441
  _globals['_VALIDATEUSERREQUEST']._serialized_end=498
  _globals['_VALIDATEUSERRESPONSE']._serialized_start=500
  _globals['_VALIDATEUSERRESPONSE']._serialized_end=538
  _globals['_DATANODESDOWNLOADREQUEST']._serialized_start=540
  _globals['_DATANODESDOWNLOADREQUEST']._serialized_end=598
  _globals['_NAMENODESERVICE']._serialized_start=601
  _globals['_NAMENODESERVICE']._serialized_end=1008
# @@protoc_insertion_point(module_scope)
