from tkinter import *
from tkinter import messagebox
import socket

mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class managerScreen(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        self.master.title("Manager")

        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.optionLabel = Label(self.frame1, text="Select your report")
        self.optionLabel.pack(padx=5, pady=5)

        self.options = ["(1) Which employee makes the highest number of reservations?",
                        "(2) Which appartment is the most popular?",
                        "(3) How many appartments are currently availible?",
                        "(4) How many appartments have not been reserved yet?"]
        self.noopt = StringVar()
        self.noopt.set(self.options[0])

        for option in self.options:
            self.optionSelection = Radiobutton(self.frame1, text=option, value=option, variable=self.noopt)
            self.optionSelection.pack(padx=5, pady=5)

        self.frame2 = Frame(self)
        self.frame2.pack(side=LEFT, padx=5, pady=5)

        self.reqst = Button(self.frame1, text="Request", command=self.requestReport)
        self.reqst.pack(padx=5, pady=5)

        self.close = Button(self.frame1, text="Close", command=self.quit)
        self.close.pack(padx=5, pady=5)

    def requestReport(self):
        option = self.noopt.get()
        msg = ("report" + option[1]).encode()
        mySocket.send(msg)
        serverMsg = mySocket.recv(1024).decode()

        msg1 = serverMsg.split(";")

        if len(msg1) <= 1:
            messagebox.showinfo("Message", "Your report had no results")
        elif option[1] == "1":
            messagebox.showinfo("Message",
                                "The Employee(s) with the highest number of reservations is/are " + ", ".join(msg1[1:]))
        elif option[1] == "2":
            messagebox.showinfo("Message", "The most popular Apartment(s) is/are " + ", ".join(msg1[1:]))
        elif option[1] == "3":
            messagebox.showinfo("Message", "The amount of appartments currently availible is " + str(msg1[1]))
        elif option[1] == "4":
            messagebox.showinfo("Message", "The amount of appartments not yet reserved is " + str(len(msg1[1:]) - 1))


class employeeScreen(Frame):

    def __init__(self, master, username):
        self.username = username
        Frame.__init__(self, master)
        self.pack()
        self.master.title("Employee")

        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.appCodeLabel = Label(self.frame1, text="Appartment Code")
        self.appCodeLabel.pack(side=LEFT, padx=5, pady=5)

        self.appCode = Entry(self.frame1, name="appcode")
        self.appCode.pack(side=LEFT, padx=5, pady=5)

        self.frame2 = Frame(self)
        self.frame2.pack(padx=5, pady=5)

        self.sDateLabel = Label(self.frame2, text="Start Date")
        self.sDateLabel.pack(side=LEFT, padx=5, pady=5)

        self.sDate = Entry(self.frame2, name="sDate")
        self.sDate.pack(side=LEFT, padx=5, pady=5)

        self.frame3 = Frame(self)
        self.frame3.pack(padx=5, pady=5)

        self.eDateLabel = Label(self.frame3, text="End Date")
        self.eDateLabel.pack(side=LEFT, padx=5, pady=5)

        self.eDate = Entry(self.frame3, name="eDate")
        self.eDate.pack(side=LEFT, padx=5, pady=5)

        self.frame4 = Frame(self)
        self.frame4.pack(padx=5, pady=5)

        self.cNameLabel = Label(self.frame4, text="Customer Name")
        self.cNameLabel.pack(side=LEFT, padx=5, pady=5)

        self.cName = Entry(self.frame4, name="cName")
        self.cName.pack(side=LEFT, padx=5, pady=5)

        self.frame5 = Frame(self)
        self.frame5.pack(padx=5, pady=5)

        self.showD = Button(self.frame5, text="Show", command=self.showDetails)
        self.showD.pack(side=LEFT, padx=5, pady=5)

        self.resV = Button(self.frame5, text="Reserve", command=self.reserve)
        self.resV.pack(side=LEFT, padx=5, pady=5)

        self.close = Button(self.frame5, text="Close", command=self.quit)
        self.close.pack(side=LEFT, padx=5, pady=5)

    def showDetails(self):
        appcode = self.appCode.get()
        sdate = self.sDate.get()
        edate = self.eDate.get()

        msg = ("apartment;" + appcode + ";" + sdate + ";" + edate).encode()

        mySocket.send(msg)
        serverMsg = mySocket.recv(1024).decode()

        if serverMsg == "invalidapartmentcode":
            messagebox.showerror("Message", "Invalid Credentials")
        else:
            msg1 = serverMsg.split(";")
            messagebox.showinfo("Message", "Appartment Code: " + msg1[1] + "\nAddress: " + msg1[2] + "\nCity: " + msg1[
                3] + "\nPostCode: " + msg1[4] + "\nSize: " + msg1[5] +
                                "\nNo Of Bedrooms: " + msg1[6] + "\nAvailibility: " + msg1[7])

    def reserve(self):
        appcode = self.appCode.get()
        sdate = self.sDate.get()
        edate = self.eDate.get()
        cname = self.cName.get()
        ename = self.username

        msg = ("reservation;" + appcode + ";" + cname + ";" + sdate + ";" + edate + ";" + ename).encode()
        mySocket.send(msg)
        serverMsg = mySocket.recv(1024).decode()

        if serverMsg == "successfulreservation":
            messagebox.showinfo("Message", "You made a succesful reservation")
        elif serverMsg == "notavailable":
            messagebox.showerror("Message", "You couldn't make a succesful reservation")
        else:
            messagebox.showerror("Message", "Invalid Appartment Code Entered")


class userLogin(Frame):

    def __init__(self, master, client):
        Frame.__init__(self, master)
        self.client = client
        self.pack()
        self.master.title("Login")

        serverMsg = self.client.recv(1024).decode()

        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.userNameLabel = Label(self.frame1, text="Username")
        self.userNameLabel.pack(side=LEFT, padx=5, pady=5)

        self.userName = Entry(self.frame1, name="username")
        self.userName.pack(side=LEFT, padx=5, pady=5)

        self.frame2 = Frame(self)
        self.frame2.pack(padx=5, pady=5)

        self.passwordLabel = Label(self.frame2, text="Password")
        self.passwordLabel.pack(side=LEFT, padx=5, pady=5)

        self.password = Entry(self.frame2, name="password", show="*")
        self.password.pack(side=LEFT, padx=5, pady=5)

        self.frame3 = Frame(self)
        self.frame3.pack(padx=5, pady=5)

        self.login = Button(self.frame3, text="Login", command=self.Login)
        self.login.pack(side=LEFT, padx=5, pady=5)

    def Login(self):
        global mySocket
        username = self.userName.get()
        password = self.password.get()

        msg = ("login;" + username + ";" + password).encode()

        mySocket.send(msg)
        serverMsg = mySocket.recv(1024).decode()

        if serverMsg == "terminate":
            self.master.destroy()

        if ("loginsuccess" in serverMsg) and ("employee" in serverMsg):
            messagebox.showinfo("Message", "Login successful\n" + "Welcome " + username + "!")
            root2 = Toplevel()
            window2 = employeeScreen(root2, username)
            self.destroy()
        elif ("loginsuccess" in serverMsg) and ("manager" in serverMsg):
            messagebox.showinfo("Message", "Login successful\n" + "Welcome " + username + "!")
            root2 = Toplevel()
            window2 = managerScreen(root2)
            self.destroy()
        else:
            messagebox.showerror("Message", "Invalid Credentials")


if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = 5000

    try:
        mySocket.connect((HOST, PORT))
    except:
        print("Call to connect failed")
        exit(1)

    root = Tk()
    root.geometry("200x130")
    window = userLogin(root, mySocket)
    window.mainloop()
