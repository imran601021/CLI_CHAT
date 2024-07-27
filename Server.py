import threading
from pickle import dumps, loads
import socket

Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 5050

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
RECEIVE = 1024
DISCONNECT = b"Disconnect"

Socket.bind(ADDR)

clients = []
nicknames = []
lock = threading.Lock()
admin_credentials = {"admin": "admin123"}  # Example admin credentials
member_credentials = {}

def broadcast(message, exclude_client=None):
    with lock:
        for client in clients:
            if client != exclude_client:
                try:
                    client.send(dumps(message))
                except Exception as e:
                    print(f"[Error] Sending message to client: {e}")

def handle_request(con, addr):
    global clients, nicknames  # Ensure we refer to the global lists
    print(f"[Connection] New connection {addr} is connected")
    connected = True
    username = None
    is_admin = False

    try:
        while True:
            credentials_data = loads(con.recv(RECEIVE))
            action = credentials_data['action']
            username = credentials_data['username']
            password = credentials_data['password']

            if action == 'register':
                if username in member_credentials or username in admin_credentials:
                    con.send(dumps("Username already exists."))
                else:
                    member_credentials[username] = password
                    con.send(dumps("Registration successful. You can now log in."))
            elif action == 'login':
                if username in admin_credentials and admin_credentials[username] == password:
                    is_admin = True
                    con.send(dumps("Admin login successful."))
                    break
                elif username in member_credentials and member_credentials[username] == password:
                    con.send(dumps("Login successful."))
                    break
                else:
                    con.send(dumps("Invalid username or password."))

        with lock:
            nicknames.append(username)
            clients.append(con)
        broadcast(f"{username} has joined the chat.")

        while connected:
            try:
                data = con.recv(RECEIVE)
                if not data:
                    break
                message = loads(data)
                if message == DISCONNECT:
                    connected = False
                    print(f"[Client] {username} has gone offline {addr}")
                    broadcast(f"{username} has left the chat.")
                else:
                    formatted_message = f"[{username}]: {message.split(': ', 1)[1]}"
                    print(f"[Message] {formatted_message}")
                    broadcast(formatted_message, exclude_client=con)
            except Exception as e:
                print(f"[Error] {e}")
                break
    finally:
        con.close()
        with lock:
            if con in clients:
                clients.remove(con)
            if username in nicknames:
                nicknames.remove(username)
        broadcast(f"{username} has left the chat.")

def start():
    Socket.listen()
    print(f"[Listening] Server is listening on {SERVER}")

    while True:
        con, addr = Socket.accept()
        thread = threading.Thread(target=handle_request, args=(con, addr))
        thread.start()
        print(f"[Connected] to {addr}")

print("[Starting] Server...")
start()

