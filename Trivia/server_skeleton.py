##############################################################################
# server.py
##############################################################################

import socket
import chatlib
import select
import random
import json
from operator import itemgetter
# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
client_sockets =[]
messages_to_send = []


ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS
def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())

def is_still_connected(sock):
    try:
        sock.sendall(b"ping")
        return True
    except:
        return False

def build_and_send_message(conn, code, msg):
    global messages_to_send

    msg = chatlib.build_message(code, msg)
    messages_to_send.append((conn ,msg))

    return


def recv_message_and_parse(conn):
    full_msg = conn.recv(1024).decode()
    cmd, data = chatlib.parse_message(full_msg)
    print("[CLIENT] ", full_msg)  # Debug print
    return cmd, data


# Data Loaders #

def load_questions():
    global questions
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """

    with open('questions.txt') as f:
        data = f.read()
    questions = json.loads(data)
    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    global users
    with open('users.txt') as f:
        data = f.read()
    users = json.loads(data)
    return

def create_random_question(username):
    global questions
    questions = load_questions()
    alredy_questioned = users[username]["questions_asked"]
    q_list = list(questions.keys())
    choices_list = list(filter(lambda x: x not in alredy_questioned, q_list))
    my_choice = random.choice(choices_list)
    my_question = (str(my_choice), questions[my_choice]["question"],*questions[my_choice]["answers"])
    return chatlib.join_data(my_question)

# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Server is up and running")
    return server_socket


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    conn.send(chatlib.build_message("ERROR", error_msg).encode())
    return


##### MESSAGE HANDLING

def handle_question_message(conn):
    build_and_send_message(conn,chatlib.PROTOCOL_SERVER["your_question"], create_random_question(logged_users[conn.getpeername()]))
    return

def handle_answer_message(conn, username, answer):
    global questions
    global users

    answer = chatlib.split_data(answer, 2)
    if questions[(answer[0])]["correct"] == eval(answer[1]):
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["correct_ans"], "")
        users[username]["score"] += 5
    else:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["wrong_ans"], str(questions[(answer[0])]["correct"]))
    return



def handle_getscore_message(conn, username):
    global users
    score = users[str(username)]["score"]
    try:
        build_and_send_message(conn, "YOUR_SCORE", str(score))
    except:
        print(ERROR_MSG)

def handle_logged_message(conn):
    global logged_users
    try:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["logged_ans"],str(logged_users))
    except:
        print(ERROR_MSG)

def handle_highscore_message (conn):
    global users
    scores ={}
    for iter in users:
        scores[iter] = users[iter]["score"]
    scores = dict(sorted(scores.items(), key=itemgetter(1), reverse=True))
    try:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["all_score"], str(scores))
    except:
        print(ERROR_MSG)

def handle_logout_message(conn):

    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    global client_sockets
    ###

    logged_users.pop(conn.getpeername())
    conn.close()
    client_sockets.remove(conn)



def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users  # To be used later

    data = chatlib.split_data(data, 2)
    if data[0] in users:
        if users[str(data[0])]["password"] == data[1]:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], "")
            addr = conn.getpeername()
            logged_users[addr] = data[0]
        else:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], "the password do not match")
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], "there is not such user")
    return


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users

    if cmd == "":
        print("connection closed!")
        conn.close()
        client_sockets.remove(conn)

    if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
        handle_login_message(conn, data)
        return
    if cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
        handle_logout_message(conn)
        return
    if cmd == chatlib.PROTOCOL_CLIENT["get_my_score"]:
        handle_getscore_message(conn, logged_users[conn.getpeername()])
        return
    if cmd == chatlib.PROTOCOL_CLIENT["logged_users"]:
        handle_logged_message(conn)
        return
    if cmd == chatlib.PROTOCOL_CLIENT["get_question"]:
        handle_question_message(conn)
        return
    if cmd == chatlib.PROTOCOL_CLIENT["high_score"]:
        handle_highscore_message(conn)
        return
    if cmd == chatlib.PROTOCOL_CLIENT["send_answer"]:
        handle_answer_message(conn ,logged_users[conn.getpeername()], data)
        return

    build_and_send_message(conn, ERROR_MSG, "the command is not in protocol")


def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global users
    global questions
    global client_sockets
    global messages_to_send

    print("Welcome to Trivia Server!")
    load_user_database()
    load_questions()
    server_socket = setup_socket()


    while True:
        try:
            ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets,
                                                                client_sockets, [])
        except:
            pass

        for current in ready_to_read:
            if current is server_socket:
                (client_socket, client_address) = current.accept()
                print("new client here", client_address)
                client_sockets.append(client_socket)

            else:
                c_cmd , c_data = recv_message_and_parse(current)
                handle_client_message(current, c_cmd, c_data)

        for message in messages_to_send:
            current_socket, data = message
            if current_socket in ready_to_write:
                current_socket.send(data.encode())
                print("[SERVER] ", data)  # Debug print

                messages_to_send.remove(message)







if __name__ == '__main__':
    main()
