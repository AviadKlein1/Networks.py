import socket
import select

MX_MSG_LENGHT = 1024
SERVER_PORT = 5555
SERVER_IP = "0.0.0.0"


def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())


def main():
    print("starting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("listening for clients...")
    client_sockets = []
    messages_to_send = []
    while True:
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets,
                                                                client_sockets, [])
        for current in ready_to_read:
            if current is server_socket:
                (client_socket, client_address) = current.accept()
                print("new client here", client_address)
                client_sockets.append(client_socket)
                print_client_sockets(client_sockets)
            else:
                print("new data from client")
                try:
                    data = current.recv(MX_MSG_LENGHT).decode()
                except:
                    print("connection closed!")
                    client_sockets.remove(current)
                    current.close()
                    print("now connect:")
                    print_client_sockets(client_sockets)
                    continue
                if data == "":
                    print("connection closed!")
                    client_sockets.remove(current)
                    current.close()
                    print("now connect:")
                    print_client_sockets(client_sockets)
                else:
                    print(data)
                    messages_to_send.append((current, data))
        for message in messages_to_send:
            current_socket, data = message
            if current_socket in ready_to_write:
                current_socket.send(data.encode())
                messages_to_send.remove(message)

    return


main()
