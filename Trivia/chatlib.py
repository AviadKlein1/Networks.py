# Protocol Constants

CMD_FIELD_LENGTH = 16	# Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10**LENGTH_FIELD_LENGTH-1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages 
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
"login_msg" : "LOGIN",
"logout_msg" : "LOGOUT",
"high_score" : "HIGHSCORE",
"get_my_score" : "MY_SCORE",
"get_question" : "GET_QUESTION",
"send_answer" : "SEND_ANSWER",
"logged_users" : "LOGGED"
} # .. Add more commands if needed


PROTOCOL_SERVER = {
"login_ok_msg" : "LOGIN_OK",
"login_failed_msg" : "ERROR",
"your_score" : "YOUR_SCORE",
"all_score" : "ALL_SCORE",
"your_question" : "YOUR_QUESTION",
"logged_ans" : "LOGGED_ANSWER",
"correct_ans" : "CORRECT_ANSWER",
"wrong_ans" : "WRONG_ANSWER"
} # ..  Add more commands if needed


# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
	"""
	Gets command name (str) and data field (str) and creates a valid protocol message
	Returns: str, or None if error occured
	"""
	if len(cmd) <= CMD_FIELD_LENGTH and len(data) < MAX_DATA_LENGTH:
		return f'{cmd:{" "}<{CMD_FIELD_LENGTH}}' + DELIMITER + f'{str(len(data)):{"0"}>{LENGTH_FIELD_LENGTH}}' + DELIMITER + data

	return ERROR_RETURN

def parse_message(data):
	"""
	Parses protocol message and returns command name and data field
	Returns: cmd (str), data (str). If some error occured, returns None, None
	"""
	if len(data) <= MAX_MSG_LENGTH and len(data) >= 0 and data.count(DELIMITER) == 2:
		dataS = data.split(DELIMITER)
		try:
			int(dataS[1]) >= 0
			if int(dataS[1]) == len(dataS[2]):
				return (dataS[0].strip(' '),dataS[2])

		except ValueError:
			return None, None
	return None, None

    # The function should return 2 values
    #return cmd, msg

	
def split_data(msg, expected_fields):
	"""
	Helper method. gets a string and number of expected fields in it. Splits the string 
	using protocol's data field delimiter (|#) and validates that there are correct number of fields.
	Returns: list of fields if all ok. If some error occured, returns None
	"""

	data = msg.split(DATA_DELIMITER)
	if len(data) == expected_fields:
		return data
	else:
		return None


def join_data(msg_fields):
	"""
	Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter. 
	Returns: string that looks like cell1#cell2#cell3
	"""
	data = DATA_DELIMITER.join(msg_fields)
	return data
