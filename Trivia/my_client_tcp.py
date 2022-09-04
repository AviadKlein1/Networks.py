import socket
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect(("127.0.0.1",8820))

data = ""
while data != "Bye":
    msg = input("Please enter your message\n")
    my_socket.send(msg.encode())
    data = my_socket.recv( 1024 ).decode()
    print( "The server sent " + data)

print("Closing client socket")
my_socket.close()