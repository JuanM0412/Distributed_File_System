# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: data_node.proto
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
    'data_node.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0f\x64\x61ta_node.proto\x12\tdata_node\"\x17\n\x05\x43hunk\x12\x0e\n\x06\x62uffer\x18\x01 \x01(\x0c\"\x17\n\x05Reply\x12\x0e\n\x06length\x18\x01 \x01(\x01\"\"\n\x0eGetFileRequest\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t2v\n\x08\x44\x61taNode\x12\x30\n\x08SendFile\x12\x10.data_node.Chunk\x1a\x10.data_node.Reply(\x01\x12\x38\n\x07GetFile\x12\x19.data_node.GetFileRequest\x1a\x10.data_node.Chunk0\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data_node_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_CHUNK']._serialized_start = 30
    _globals['_CHUNK']._serialized_end = 53
    _globals['_REPLY']._serialized_start = 55
    _globals['_REPLY']._serialized_end = 78
    _globals['_GETFILEREQUEST']._serialized_start = 80
    _globals['_GETFILEREQUEST']._serialized_end = 114
    _globals['_DATANODE']._serialized_start = 116
    _globals['_DATANODE']._serialized_end = 234
# @@protoc_insertion_point(module_scope)
