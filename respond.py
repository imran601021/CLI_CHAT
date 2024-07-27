import socket
import threading
from pickle import dumps, loads

RECEIVE = 1024

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050

Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Client.connect((SERVER, PORT))
DISCONNECT = b"Disconnect"

def receive():
    while True:
        try:
            message = Client.recv(RECEIVE)
            if message:
                print(loads(message))
        except Exception as e:
            print(f"An error occurred in receive: {e}")
            Client.close()
            break

def write(username):
    while True:
        try:
            message = f'{username}: {input("")}'
            Client.send(dumps(message))
        except Exception as e:
            print(f"An error occurred in write: {e}")
            Client.close()
            break

def authenticate():
    while True:
        user_type = input("Are you an admin or member? (admin/member): ").lower()
        action = input("Do you want to login or register? (login/register): ").lower()
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        auth_data = {
            'action': action,
            'username': username,
            'password': password,
            'user_type': user_type
        }
        Client.send(dumps(auth_data))
        response = loads(Client.recv(RECEIVE))
        print(response)
        if response == "Admin login successful." or response == "Login successful.":
            return username, user_type

username, user_type = authenticate()

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write, args=(username,))
write_thread.start()

