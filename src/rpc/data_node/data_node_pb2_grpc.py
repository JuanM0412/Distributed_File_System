# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from . import data_node_pb2 as data__node__pb2

GRPC_GENERATED_VERSION = '1.66.1'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in data_node_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class DataNodeStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendFile = channel.stream_unary(
                '/data_node.DataNode/SendFile',
                request_serializer=data__node__pb2.Chunk.SerializeToString,
                response_deserializer=data__node__pb2.Reply.FromString,
                _registered_method=True)
        self.GetFile = channel.unary_stream(
                '/data_node.DataNode/GetFile',
                request_serializer=data__node__pb2.GetFileRequest.SerializeToString,
                response_deserializer=data__node__pb2.Chunk.FromString,
                _registered_method=True)


class DataNodeServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendFile(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DataNodeServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendFile': grpc.stream_unary_rpc_method_handler(
                    servicer.SendFile,
                    request_deserializer=data__node__pb2.Chunk.FromString,
                    response_serializer=data__node__pb2.Reply.SerializeToString,
            ),
            'GetFile': grpc.unary_stream_rpc_method_handler(
                    servicer.GetFile,
                    request_deserializer=data__node__pb2.GetFileRequest.FromString,
                    response_serializer=data__node__pb2.Chunk.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'data_node.DataNode', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('data_node.DataNode', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class DataNode(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendFile(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(
            request_iterator,
            target,
            '/data_node.DataNode/SendFile',
            data__node__pb2.Chunk.SerializeToString,
            data__node__pb2.Reply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetFile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/data_node.DataNode/GetFile',
            data__node__pb2.GetFileRequest.SerializeToString,
            data__node__pb2.Chunk.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)