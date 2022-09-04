import socket

import chatlib

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


def get_logged_users(conn):
    r_cmd, r_data = build_send_recv_parse(conn, "LOGGED ", "")
    if r_cmd != chatlib.PROTOCOL_SERVER["logged_ans"]:
        error_and_exit("ERROR! not good answer from server")
    print("\nthe list of users: " + r_data)


def play_question(conn):
    r_cmd, r_data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_question"], "")
    if r_cmd == "NO_QUESTIONS":
        error_and_exit("EXIT! there is no more questions")
    if r_cmd != chatlib.PROTOCOL_SERVER["your_question"]:
        error_and_exit("ERROR! not good answer from server")
    parse_message = chatlib.split_data(r_data, 6)
    ID = parse_message[0]

    print("\nyour question: ")
    print(parse_message)

    user_answer = input("\nenter the number of the right answer!")
    t_cmd, t_data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["send_answer"],
                                          chatlib.join_data((ID, user_answer)))
    if t_cmd == "CORRECT_ANSWER":
        print("correct answer!")
    if t_cmd == "WRONG_ANSWER":
        print("wrong answer!\n the correct answer is: " + t_data)
    return


def build_send_recv_parse(conn, code, data):
    build_and_send_message(conn, code, data)
    return recv_message_and_parse(conn)


def get_score(conn):
    r_cmd, r_data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_my_score"], "")
    if r_cmd != chatlib.PROTOCOL_SERVER["your_score"]:
        error_and_exit("ERROR! not good answer")
    print("your score: " + r_data)
    return


def get_highScore(conn):
    r_cmd, r_data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["high_score"], "")
    if r_cmd != chatlib.PROTOCOL_SERVER["all_score"]:
        error_and_exit("ERROR! not good answer")
    print("high score: " + r_data)
    return


def build_and_send_message(conn, code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    msg = chatlib.build_message(code, data)
    conn.send(msg.encode())
    print(msg)
    return


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket,
    then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """
    full_msg = conn.recv(1024).decode()
    cmd, data = chatlib.parse_message(full_msg)
    return cmd, data


def connect():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((SERVER_IP, SERVER_PORT))
    return my_socket


def error_and_exit(error_msg):
    print(error_msg)
    exit()


def login(conn):
    while True:
        username = input("Please enter username: \n")
        password = input("Please enter password: \n")
        data = username + "#" + password
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], data)
        recive_data = recv_message_and_parse(conn)
        print(recive_data)
        if recive_data[0] == chatlib.PROTOCOL_SERVER["login_ok_msg"]: break
    return


def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")
    recive_data = recv_message_and_parse(conn)
    print(recive_data)
    return


def main():
    conn = connect()
    login(conn)
    print("\n----\n"
          "welcome!\n")

    while True:
        print("for your score enter 1\n"
              "for the score table enter 2\n"
              "for the logged users enter 3\n"
              "to play enter 4\n"
              "to exit enter 9\n")
        user_input = input("please choose number of command:")
        if eval(user_input) == 1:
            get_score(conn)
        elif eval(user_input) == 2:
            get_highScore(conn)
        elif eval(user_input) == 3:
            get_logged_users(conn)
        elif eval(user_input) == 4:
            play_question(conn)
        elif eval(user_input) == 9:
            logout(conn)
            exit()
        else:
            print("\nchoose one of the options!\n")
    return


if __name__ == '__main__':
    main()
