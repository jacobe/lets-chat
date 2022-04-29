import logging
import signal
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
        session_id = str(response.token)

        def shutdown(signum, frame):
            print("Logging out...")
            stub.Logout(chat_pb2.LogoutRequest(token=session_id))
            exit(0)
        signal.signal(signal.SIGINT, shutdown)

        while (True):
            line = input("> ")
            # TODO: Send message over stream


if __name__ == "__main__":
    logging.basicConfig()
    run()
