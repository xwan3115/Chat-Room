# Python 3
# Usage: python3 UDPClient3.py localhost 12000
# coding: utf-8
import sys
from socket import *
import threading
import time
import datetime as dt

# The argument of client
servername = sys.argv[1]
serverPort = sys.argv[2]
udpPort = sys.argv[3]
serverPort = int(serverPort)

# Create the TCP socket
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((servername, serverPort))

# Create the UDP socket
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
portnum = int(udpPort)
udpsock = socket(AF_INET, SOCK_DGRAM)
udpsock.bind((local_ip, udpPort))


# Start a thread for UDP transfer
def udprec():
    while (True):

        # We receive the filename first
        l, addr = udpsock.recvfrom(1024)

        # Save the filename if file name is not defined
        filename = ''
        if not filename:
            filename = l.decode('utf-8')
            l = ''

        # Next the
        while (l):
            f = open(filename, a)
            f.write(l)
            f.close()
            l, addr = udpsock.recvfrom(1024)


thread = threading.Thread(target=udprec)
thread.start()


# This is the authentication function
# It process the reply info comes from the server
def authenticate():
    while True:
        receivedMessage = clientSocket.recv(2048)
        receivedMessage = receivedMessage.decode('utf-8')

        if receivedMessage == "Username\r\n":
            message = input("Username: ")
            clientSocket.send(message.encode('utf-8'))

        elif receivedMessage == "Password\r\n":
            message = input("Password: ")
            clientSocket.send(message.encode('utf-8'))

        elif receivedMessage == "Invalid Password\r\n":
            print("Invalid Password. Please try again\n")
            message = input("Password: ")
            clientSocket.send(message.encode('utf-8'))

        # If return False, it means you are locked.
        elif receivedMessage == "Locked\r\n":
            print("Invalid Password. Your account has been blocked. Please try again later\n")
            return False

        elif receivedMessage == "Still locked\r\n":
            print("Your account is blocked due to multiple login failures. Please try again later\n")
            return False

        elif receivedMessage == "Login Success\r\n":
            clientSocket.send(udpPort.encode('utf-8'))
            return True


# Respond to message sent by the dlt function in server
def msg(word):
    # print(clientSocket)
    confirm = clientSocket.recv(2048).decode('utf-8')
    confirm = confirm.split()
    time = ' '.join(confirm[1::])
    message = 'Message ' + '#' + confirm[0] + ' ' + 'posted at ' + time + '.\n'
    print(message)


# Respond to message sent by the dlt function in server
def dlt(infor):
    infor = infor.split()
    info = infor[0]
    if info == 'Seq':
        print('The sequence number you provided is invalid\n')
    elif info == 'User':
        print('You do not have the authority to delete this message\n')
    elif info == 'Timestamp':
        print('The timestamp you provided does not match the log. Please check\n')
    elif info == 'Delete':
        time = ' '.join(infor[1::])
        print('The deletion at ' + time + ' is successful\n')


# Respond to message sent by the dlt function in server
def edt(infor):
    infor = infor.split()
    info = infor[0]
    if info == 'Seq':
        print('The sequence number you provided is invalid\n')
    elif info == 'User':
        print('You do not have the authority to delete this message\n')
    elif info == 'Timestamp':
        print('The timestamp you provided does not match the log. Please check\n')
    elif info == 'Edit':
        print("enter\n")
        time = ' '.join(infor[1::])
        print('The Edit operation at ' + time + ' is successful\n')


def upd():
    pass


# The authenticate function will retrun true or false
# If true, the welcome message will print
ifloged = authenticate()
while ifloged:
    print("Welcome to TOOM!")
    allcommand = input("Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD):")
    command = allcommand[0:3]

    if command == 'MSG':

        # Check the usage of this command
        if allcommand == 'MSG':
            print("Error! Need message after MSG command\n")
        else:
            clientSocket.send(allcommand.encode('utf-8'))
            msg(allcommand[4::])
    elif command == 'DLT':

        # We need to check the usage of DLT
        if allcommand == 'DLT':
            print("Error! Need seq number and timestamp after DLT command\n")
        else:
            clientSocket.send(allcommand.encode('utf-8'))
            info = allcommand[4::]
            lists = info.split()
            if len(lists) <= 2:
                print("Error! Need seq number and timestamp after DLT command\n")
            else:
                recev = clientSocket.recv(2048).decode('utf-8')
                dlt(recev)

    elif command == 'EDT':
        if allcommand == 'EDT':
            print("Error! Need seq number, timestamp, and modified message after EDT command\n")
        else:
            info = allcommand[4::]
            lists = info.split()
            if len(lists) <= 2:
                print("Error! Need seq number, timestamp, and modified message after EDT command\n")
            else:
                clientSocket.send(allcommand.encode('utf-8'))
                recev = clientSocket.recv(2048).decode('utf-8')
                edt(recev)
    elif command == 'RDM':
        if allcommand == 'RDM':
            print("Error! Need timestamp after EDT command\n")
        else:
            info = allcommand[4::]
            clientSocket.send(allcommand.encode('utf-8'))
            recev = clientSocket.recv(2048).decode('utf-8')
            print(recev)
    elif command == 'ATU':
        if allcommand == command:
            clientSocket.send('ATU'.encode('utf-8'))
            print('The active user list returned: \n')
            info = clientSocket.recv(2048).decode('utf-8')
        else:
            print("Error! ATU command does not take any argument.\n")
    elif command == 'UPD':
        if allcommand == 'UPD':
            print("Error! Need filename and username after MSG command\n")
        else:
            info = allcommand[4::]
            info = info.split()

            # The username and filename
            recevname = info[0]
            file = info[-1]

            # The new filename
            filename = '_'.join(info)

            # Need to check if the username if online
            clientSocket.send(recevname.encode('utf-8'))
            msg = clientSocket.recv(1024).decode('utf-8')

            # If offline, then print offline
            if msg == 'Offline':
                print(recevname +' is offline\n')
            else:

                # First we send the filename to the audience
                udpsock.sendto(filename.encode('utf-8'), (msg[0], int(msg[1])))
                msg = msg.split()
                f = open(file, 'rb')
                line = f.read(1024)
                while (line):
                    udpsock.sendto(line, (msg[0], msg[1]))
                    line = f.read(1024)
                udpsock.close()
    elif command == 'OUT':
        if allcommand == command:
            clientSocket.send('OUT'.encode('utf-8'))
            info = clientSocket.recv(2048).decode('utf-8')
            print("Thank you for using. You have logged out.\n")
            break
        else:
            print("Error! OUT command does not take any argument.\n")

    else:
        print("This command is invalid. Please try again with either one of MSG, DLT, EDT, RDM, ATU, OUT and UPD\n")
clientSocket.close()
