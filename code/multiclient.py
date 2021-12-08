#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8
from socket import *
import sys

# The argument of client
servername = sys.argv[1]
serverPort = sys.argv[2]
udpPort = sys.argv[3]
serverPort = int(serverPort)

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((servername, serverPort))
def authenticate():
    while True:
        receivedMessage = clientSocket.recv(2048)
        receivedMessage = receivedMessage.decode('utf-8')
        if receivedMessage == "Username\r\n":
            message = input("Username: ")
            clientSocket.sendall(message.encode('utf-8'))
        elif receivedMessage == "Password\r\n":
            message = input("Password: ")
            clientSocket.sendall(message.encode('utf-8'))
        elif receivedMessage == "Invalid Password\r\n":
            print("Invalid Password. Please try again\n")
            message = input("Password: ")
            clientSocket.sendall(message.encode('utf-8'))
        elif receivedMessage == "Locked\r\n":
            print("Invalid Password. Your account has been blocked. Please try again later\n")
            return False
        elif receivedMessage == "Still locked\r\n":
            print("Your account is blocked due to multiple login failures. Please try again later\n")
            return False
        elif receivedMessage == "Login Success\r\n":
            clientSocket.sendall(udpPort.encode('utf-8'))
            return True

def msg(word):
    clientSocket.sendall(word.encode('utf-8'))
    confirm = clientSocket.recv(2048).decode('utf-8')
    confirm = confirm.split()
    time = ' '.join(confirm[1::])
    message = 'Message ' + '#' + confirm[0] + ' ' + 'posted at ' + time +'.\n'
    print(message)

def dlt(info):
    if info == 'Seq':
        print('The sequence number you provided is invalid\n')
    elif info == 'User':
        print('You do not have the authority to delete this message\n')
    elif info == 'Timestamp':
        print('The timestamp you provided does not match the log. Please check\n')
    elif info == 'Delete':
        time = clientSocket.recv(2048).decode('utf-8')
        print('The deletion at '+time+' is successful\n')

def edt(info):
    if info == 'Seq':
        print('The sequence number you provided is invalid\n')
    elif info == 'User':
        print('You do not have the authority to delete this message\n')
    elif info == 'Timestamp':
        print('The timestamp you provided does not match the log. Please check\n')
    elif info == 'Edit':
        time = clientSocket.recv(2048).decode('utf-8')
        print('The deletion at ' + time + ' is successful\n')

def upd():
    pass

ifloged = authenticate()
while ifloged:
    print("Welcome to TOOM!")
    allcommand = input("Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD):")
    command = allcommand[0:3]
    if command == 'MSG':
        if allcommand == 'MSG':
            print("Error! Need message after MSG command\n")
        else:
            clientSocket.sendall('MSG'.encode('utf-8'))
            msg(allcommand[4::])
    elif command == 'DLT':
        # We need to check the usage of DLT
        if allcommand == 'DLT':
            print("Error! Need seq number and timestamp after DLT command\n")
        else:
            clientSocket.sendall('DLT'.encode('utf-8'))
            info = allcommand[4::]
            lists = info.split()
            if len(lists) <= 2:
                print("Error! Need seq number and timestamp after DLT command\n")
            else:
                clientSocket.sendall(info.encode('utf-8'))
                recev = clientSocket.recv(2048).decode('utf-8')
                dlt(recev)

    elif command == 'EDT':
        if allcommand == 'EDT':
            print("Error! Need seq number, timestamp, and modified message after EDT command\n")
        else:
            clientSocket.sendall('EDT'.encode('utf-8'))
            info = allcommand[4::]
            lists = info.split()
            if len(lists) <= 2:
                print("Error! Need seq number, timestamp, and modified message after EDT command\n")
            else:
                clientSocket.sendall(info.encode('utf-8'))
                recev = clientSocket.recv(2048).decode('utf-8')
                edt(recev)
    elif command == 'RDM':
        if allcommand == 'RDM':
            print("Error! Need timestamp after EDT command\n")
        else:
            clientSocket.sendall('RDM'.encode('utf-8'))
            info = allcommand[4::]
            clientSocket.sendall(info.encode('utf-8'))
            recev = clientSocket.recv(2048).decode('utf-8')
            print(recev)
    elif command == 'ATU':
        if allcommand == command:
            clientSocket.sendall('ATU'.encode('utf-8'))
            print('The active user list returned: \n')
            info = clientSocket.recv(2048).decode('utf-8')
            print(info)
        else:
            print("Error! ATU command does not take any argument.\n")
    elif command == 'UPD':
        pass
    elif command == 'OUT':
        if allcommand == command:
            clientSocket.sendall('OUT'.encode('utf-8'))
            info = clientSocket.recv(2048).encode('utf-8')
            print("Thank you for using. You have logged out.\n")
            break
        else:
            print("Error! OUT command does not take any argument.\n")


    else:
        print("This command is invalid. Please try again with either one of MSG, DLT, EDT, RDM, ATU, OUT and UPD\n")



clientSocket.close()