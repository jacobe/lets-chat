import logging
import grpc
import chat_pb2
import chat_pb2_grpc


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = chat_pb2_grpc.ChatStub(channel)
        name = input("Enter your name")
        password = input("Enter your password")
        response = stub.Login(chat_pb2.LoginRequest(password=password, name=name))
        print("Login request received: " + str(response))


if __name__ == "__main__":
    logging.basicConfig()
    run()
