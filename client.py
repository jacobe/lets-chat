import logging
import signal
import grpc
import chat_pb2
import chat_pb2_grpc


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = chat_pb2_grpc.ChatStub(channel)

        name = "Jacob" #input("Enter your name")
        password = "123" # input("Enter your password")
        response = stub.Login(chat_pb2.LoginRequest(password=password, name=name))
        session_id = str(response.token)
        print("Login request received: " + session_id)

        def shutdown(signum, frame):
            print("Logging out...")
            stub.Logout(chat_pb2.LogoutRequest(token=session_id))
            exit(0)
        signal.signal(signal.SIGINT, shutdown)

        for response in stub.Stream(repl(session_id)):
            if response.client_message is not None:
                print(f"\n{response.client_message.name} > {response.client_message.message}")


def repl(session_id):
    while (True):
        line = input("> ")
        yield chat_pb2.StreamRequest(message=line)
        # metadata={'x-chat-token': session_id}


if __name__ == "__main__":
    logging.basicConfig()
    run()
