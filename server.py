# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures
from datetime import datetime
import logging
from google.protobuf.timestamp_pb2 import Timestamp
import uuid

import grpc
import chat_pb2
import chat_pb2_grpc

password = "123"
sessions = dict()


class Chat(chat_pb2_grpc.ChatServicer):
    def Login(self, request, context):
        if request.password != password:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Bad password")
            raise ValueError("Bad password")
        session_id = str(uuid.uuid4())
        name = request.name
        sessions[session_id] = name
        return chat_pb2.LoginResponse(token=session_id)

    def Stream(self, request_iterator, context):
        for request in request_iterator:
            metadata = dict(request.invocation_metadata())
            authorize(metadata.get('x-chat-token'), context)

            print(request.message)
            timestamp = Timestamp()
            timestamp.GetCurrentTime()
            response = chat_pb2.StreamResponse(
                timestamp=timestamp,
                client_message = chat_pb2.StreamResponse.Message(
                    name = "tester",
                    message = str(request.message))
                )
            yield response


    def Logout(self, request, context):
        session_id = request.token
        authorize(session_id, context)
        del sessions[session_id]
        return chat_pb2.LogoutResponse()


def authorize(token, context):
    if not token or token not in sessions:
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details("Bad token")
        raise ValueError("Unauthenticated")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
