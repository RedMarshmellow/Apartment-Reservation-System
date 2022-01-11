import datetime  # used for comparing dates in reservation
import threading
import socket

userList = {}
aptList = {}
reserveList = []
lock = threading.RLock()


def update_reservations():  # custom function to re-access reservations file as it gets updated
    with open("reservations.txt", "r") as file:
        for line in file:
            line = line.rstrip()
            data = line.split(";")
            reserveList.append(data)


def is_available(code, start, end):  # cusotm function to check date overlaps
    update_reservations()
    occupied = False
    temp = start.split("/")
    temp.reverse()
    begin = datetime.date(int(temp[0]), int(temp[1]), int(temp[2]))  # split string and order at as year-month-day
    temp = end.split("/")
    temp.reverse()
    until = datetime.date(int(temp[0]), int(temp[1]), int(temp[2]))
    for res in reserveList:
        if res[0] == code:
            temp = res[2].split("/")
            temp.reverse()
            res_start = datetime.date(int(temp[0]), int(temp[1]), int(temp[2]))
            temp = res[3].split("/")
            temp.reverse()
            res_end = datetime.date(int(temp[0]), int(temp[1]), int(temp[2]))
            occupied = ((res_start <= begin <= res_end) or (res_start <= until <= res_end)) or (
                    (begin <= res_start <= until) or (
                        begin <= res_end <= until))  # check if a reservation overlaps with the entered date
    return not occupied


def reserve(params):  # function to append reservatiosn file with new reservation
    fptr = open("reservations.txt", "a")
    fptr.write(";".join(params) + "\n")
    fptr.close()


def most_reservations():  # function returns a list of employees with the maximum number of reservations
    employee_score = {}
    with open("reservations.txt", "r") as file:
        for line in file:
            line = line.rstrip()
            data = line.split(";")
            if data[4] in employee_score:
                employee_score[data[4]] += 1
            else:
                employee_score[data[4]] = 1
    max_res = max(employee_score, key=employee_score.get)
    employee_list = [max_res]
    for employee in employee_score:
        if employee_score[employee] == employee_score[max_res] and employee != max_res:
            employee_list.append(employee)
    return ";".join(employee_list)


def popular_apartments():  # function returns list of apartments with max number of reservation
    apartment_score = {}
    with open("reservations.txt", "r") as file:
        for line in file:
            line = line.rstrip()
            data = line.split(";")
            if data[0] in apartment_score:
                apartment_score[data[0]] += 1
            else:
                apartment_score[data[0]] = 1
    max_res = max(apartment_score, key=apartment_score.get)
    apartment_list = [max_res]
    for apartment in apartment_score:
        if apartment_score[apartment] == apartment_score[max_res] and apartment != max_res:
            apartment_list.append(apartment)
    return ";".join(apartment_list)


def not_reserved():  # returns a list of apartment codes that have no reservations
    unreserved = []
    for apt in aptList:
        i = apt
        found = False
        with open("reservations.txt", "r") as file:
            for line in file:
                line = line.rstrip()
                data = line.split(";")
                found = apt == data[0]
                if found:
                    break
        if not found:
            unreserved.append(i)
    return ";".join(unreserved)


class ClientThread(threading.Thread):
    def __init__(self, client_address, client_socket):
        threading.Thread.__init__(self)
        self.clientAddress = client_address
        self.clientSocket = client_socket
        self.client_msg = ""
        self.user = ""

    def run(self):
        print("connected")
        msg = "connectionsuccess".encode()
        self.clientSocket.send(msg)
        self.client_msg = self.clientSocket.recv(1024).decode()
        self.client_msg = self.client_msg.split(";")
        while self.client_msg[0] != "terminate":
            if self.client_msg[0] == "login":
                lock.acquire()
                if self.client_msg[1] in userList:
                    if self.client_msg[2] == userList[self.client_msg[1]][0]:
                        msg = ("loginsuccess" + ";" + self.client_msg[1] + ";" + userList[self.client_msg[1]][
                            1]).encode()
                        self.clientSocket.send(msg)
                    else:
                        msg = "loginfailure".encode()
                        self.clientSocket.send(msg)
                else:
                    msg = "loginfailure".encode()
                    self.clientSocket.send(msg)
                lock.release()
            elif self.client_msg[0] == "apartment":
                lock.acquire()
                if self.client_msg[1] in aptList:
                    msg = ("apartment;" + self.client_msg[1] + ";" + aptList[self.client_msg[1]][0] + ";" +
                           aptList[self.client_msg[1]][
                               1] + ";" + aptList[self.client_msg[1]][2] + ";" + aptList[self.client_msg[1]][3] + ";" +
                           aptList[self.client_msg[1]][4] + ";" + str(
                                is_available(self.client_msg[1], self.client_msg[2],
                                             self.client_msg[3]))).encode()
                    self.clientSocket.send(msg)
                else:
                    msg = "invalidapartmentcode".encode()
                    self.clientSocket.send(msg)
                lock.release()
            elif self.client_msg[0] == "reservation":
                lock.acquire()
                if self.client_msg[1] in aptList:
                    if is_available(self.client_msg[1], self.client_msg[3], self.client_msg[4]):
                        reserve(self.client_msg[1:])
                        msg = "successfulreservation".encode()
                        self.clientSocket.send(msg)
                    else:
                        msg = "notavailable".encode()
                        self.clientSocket.send(msg)
                else:
                    msg = "invalidapartmentcode".encode()
                    self.clientSocket.send(msg)
                lock.release()
            elif self.client_msg[0] == "report1":
                lock.acquire()
                msg = ("report1;" + most_reservations()).encode()
                self.clientSocket.send(msg)
                lock.release()
            elif self.client_msg[0] == "report2":
                lock.acquire()
                msg = ("report2;" + popular_apartments()).encode()
                self.clientSocket.send(msg)
                lock.release()
            elif self.client_msg[0] == "report3":
                lock.acquire()
                msg = ("report3;" + str(len(aptList))).encode()
                self.clientSocket.send(msg)
                lock.release()
            elif self.client_msg[0] == "report4":
                lock.acquire()
                msg = ("report4;" + not_reserved()).encode()
                self.clientSocket.send(msg)
                lock.release()
            self.client_msg = self.clientSocket.recv(1024).decode()
            self.client_msg = self.client_msg.split(";")
        msg = "connectionterminated".encode()
        self.clientSocket.send(msg)
        self.clientSocket.close()


if __name__ == "__main__":
    with open("users.txt", "r") as file:  # read and parse users file
        for line in file:
            line = line.rstrip()
            data = line.split(";")
            userList[data[0]] = [data[1], data[2]]
    with open("apartments.txt", "r") as file:  # read and parse apartments file
        for line in file:
            line = line.rstrip()
            data = line.split(";")
            aptList[data[0]] = [data[1], data[2], data[3], data[4], data[5]]
    update_reservations()  # read and parse reservations file, custom function used due to frequesnt updating required
    HOST = "127.0.0.1"  # socket configuration
    PORT = 5000
    Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        Socket.bind((HOST, PORT))  # attempt bind
    except socket.error:
        print("Call to bind failed")
        exit(1)

    while True:
        Socket.listen()  # await connection attempt
        connection, address = Socket.accept()
        new_thread = ClientThread(address, connection)  # create new thread object for client connection
        new_thread.start()
