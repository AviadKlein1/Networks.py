import socket
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SERVER_IP = "127.0.0.1"
PORT = 8821
MAX_MSG_SIZE = 1024

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data=""
while True:
    my_socket.sendto(input("enter massage").encode(), (SERVER_IP, PORT))
    (response, remote_address) = my_socket.recvfrom(MAX_MSG_SIZE)
    data = response.decode()
    if data =="BYE!":
        break
    print("\nThe server sent " + data)
print("the connection is closed")
my_socket.close()
