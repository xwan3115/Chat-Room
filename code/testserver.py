# Python 3
# coding: utf-8
import sys
from socket import *
import threading
import time
import datetime as dt

# Read port number and number of failed attempt from sys argv
serverPort = sys.argv[1]
nb_failed = sys.argv[2]
serverPort = int(serverPort)
nb_failed = int(nb_failed)

# The nb of failed attempt should in the range of 1-5
while nb_failed > 5 or nb_failed <= 0:
    nb_failed = input("The allowable attempts should be between 1 and 5: ")

# The client log in information is inside this array
# We store it for later authentication use
credentials = {}
with open('Credentials.txt') as f:
    for line in f:
        line = line.strip()
        value = line.split()
        credentials[value[0]] = value[1]

# This dict will contain info about blocked account
blocklist = {}

# We also need store the information of message log and user log
logseq = 0
msgseq = 0
msglogall = []
userlog = []

# We need to create the log files in case they do not exists (overwrite every time the server starts)
f = open("userlog.txt", 'w')
f.close()
f = open('messagelog.txt', 'w')
f.close()

# This is the authentication process
def authentication(client_sock, addr):
    global nb_failed
    global credentials
    global blocklist
    global logseq
    global userlog
    attempt = 0

    # We ask for the username and check if it is correct
    name = False

    # I also checked if the username is valid
    # However, the test case will not include this situation
    while not name:
        client_sock.send("Username\r\n".encode('utf-8'))
        username = client_sock.recv(2048)
        username = username.decode()
        if username not in credentials:
            attempt += 1
            if attempt == nb_failed:
                client_sock.send("Locked\r\n".encode('utf-8'))
                return 1
            client_sock.send("Invalid username\r\n".encode('utf-8'))
        else:
            name = True
            client_sock.send("Password\r\n".encode('utf-8'))

    # If the username is correct, we then check if the password is correct
    passw = False
    while not passw:
        password = client_sock.recv(2048)
        password = password.decode()

        # If this account is in the block list
        # We test if the timestamp has passed 10 seconds
        if username in blocklist:
            if dt.datetime.now() <= blocklist[username]:
                client_sock.send("Still locked\r\n".encode('utf-8'))
                client_sock.close()
                return 1
            else:
                # If the block time has passed, we remove this account from block list
                del blocklist[username]

        # Next we check the password
        if credentials[username] == password:
            client_sock.send("Login Success\r\n".encode('utf-8'))

            # The log in is successful and then we need seq number, timestamp, username, host and udp port number
            udpport = client_sock.recv(2048)
            udpport = udpport.decode('utf-8')
            host, port = client_sock.getpeername()
            currtime = dt.datetime.now()
            date_time = currtime.strftime("%d %b %Y %H:%M:%S")
            logseq += 1

            # We have all the info, then write them into the log
            logEntry = str(logseq) + '; ' + date_time + '; ' + username + '; ' + str(host) + '; ' + udpport + '\n'
            f = open('userlog.txt', 'a')
            f.write(logEntry)
            f.close()

            # We also save a copy in a list we defined (for later use)
            entry = '; ' + date_time + '; ' + username + '; ' + str(host) + '; ' + udpport + '\n'
            userlog.append(entry)
            return username
        else:
            attempt += 1
            if attempt >= nb_failed:
                client_sock.send("Locked\r\n".encode('utf-8'))

                # We add 10 seconds to the timestamp so we can compare it directly with the current time
                blocklist[username] = dt.datetime.now() + dt.timedelta(seconds=10)
                client_sock.close()
                return False
            client_sock.send("Invalid Password\r\n".encode('utf-8'))

# This function is used to add the posted message to the log file
def msg(client_sock, info, username):
    global msgseq
    global msglogall

    # We need seq number, timestamp, and edited info so we can write into the file
    msgseq += 1
    currtime = dt.datetime.now()
    date_time = currtime.strftime("%d %b %Y %H:%M:%S")
    edited = 'no'

    # save them into the list (for later use)
    entry = '; ' + date_time + '; ' + username + '; ' + info + '; ' + edited + '\n'
    msglogall.append(entry)

    # Write this message into the file
    logentry = str(msgseq) + '; ' + date_time + '; ' + username + '; ' + info + '; ' + edited + '\n'
    f = open('messagelog.txt', 'a')
    f.write(logentry)
    f.close()

    # Send a confirm message to the user and print this operation
    confirm = str(msgseq) + ' ' + date_time
    client_sock.send(confirm.encode('utf-8'))
    servermsg = username + ' posted MSG #' + str(msgseq) + ' ' + '"' + info + '"' + ' at ' + date_time + '\n'
    print(servermsg)

# This function is used to delete the message
def dlt(client_sock, times, seq, user):
    global msglogall
    global msgseq

    date_time = dt.datetime.now()
    currtime = date_time.strftime("%d %b %Y %H:%M:%S")

    # First, we check if the sequence number of the message is valid
    seq = int(seq)
    seq = seq - 1
    if seq >= len(msglogall) or seq < 0:
        print(user + " trys to delete MSG #" + str(
            seq + 1) + " at " + currtime + " but failed. Reason: Invalid sequence number\n")
        client_sock.send('Seq'.encode('utf-8'))
        return

    # If seq is correct, we check the user
    entry = msglogall[seq].split('; ')
    if entry[2] != user:
        print(
            user + " trys to delete MSG #" + str(
                seq + 1) + " at " + currtime + " but failed. Reason: Authorisation fails\n")
        client_sock.send('User'.encode('utf-8'))
        return

    # Then timestamp
    if entry[1] != times:
        print(user + " trys to delete MSG #" + str(
            seq + 1) + " at " + currtime + " but failed. Reason: Invalid timestamp\n")
        client_sock.send('Timestamp'.encode('utf-8'))
        return

    # All matches. We delete the message
    del msglogall[seq]
    msgseq -= 1
    print(user + " deletes MSG #" + str(seq + 1) + " at " + currtime + "\n")
    client_sock.send('Delete'.encode('utf-8'))
    client_sock.send(currtime.encode('utf-8'))

    # Write the updated msg list into the file (All the index will now automatically corrected
    f = open('messagelog.txt', 'w')
    index = 0
    for i in msglogall:
        index += 1
        f.write(str(index) + i)
    f.close()

# This function is used to edit the posted message
# Very similar to DLT
def edt(client_sock, times, seq, user, msge):
    global msglogall
    date_time = dt.datetime.now()
    currtime = date_time.strftime("%d %b %Y %H:%M:%S")

    # First, we check if the sequence number of the message is valid
    seq = int(seq)
    seq = seq - 1
    if seq >= len(msglogall) or seq < 0:
        print(user + " trys to edit MSG #" + str(
            seq + 1) + " at " + currtime + " but failed. Reason: Invalid sequence number\n")
        client_sock.send('Seq'.encode('utf-8'))
        return

    # If seq is correct, we check the user
    entry = msglogall[seq].split('; ')
    if entry[2] != user:
        print(
            user + " trys to edit MSG #" + str(
                seq + 1) + " at " + currtime + " but failed. Reason: Authorisation fails\n")
        client_sock.send('User'.encode('utf-8'))
        return

    # Then timestamp
    if entry[1] != times:
        print(user + " trys to edit MSG #" + str(
            seq + 1) + " at " + currtime + " but failed. Reason: Invalid timestamp\n")
        client_sock.send('Timestamp'.encode('utf-8'))
        return

    # All matches. We delete the message
    msglogall[seq] = '; ' + currtime + '; ' + user + '; ' + msge + '; ' + 'Yes' + '\n'
    print(user + " edit MSG #" + str(seq + 1) + ' ' + '"' + msge + '"' + " at " + currtime + "\n")
    confirm = 'Edit ' + currtime
    client_sock.send(confirm.encode('utf-8'))

    # Write the updated msg list into the file (All the index will now automatically corrected
    f = open('messagelog.txt', 'w')
    index = 0
    for i in msglogall:
        index += 1
        f.write(str(index) + i)
    f.close()

# This is the implementation of the rdm function
def rdm(times):
    global msglogall
    index = 0
    result = ''

    # We went through every element in the msglogall list
    # It contains all the information in the messagelog.txt
    for entry in msglogall:
        index += 1
        entrylist = entry.split('; ')
        stamp = entrylist[1]

        # We can directly check if the time satisfy
        if stamp > times:
            result += str(index) + entry

    # We have to go throuh the whole list becase there might be modified message with new time stamp
    if result == '':
        result = 'No new message since ' + times + '\n'
    return result

# The atu command will tell you what is the current active user
def atu(user):
    global userlog
    result = ''

    # If there is only one user (which is the user him/herself), return
    if len(userlog) == 1:
        result = 'No other active user\n'
        print(result)
        return result
    index = 0

    # Go through the whole list and skip the user him/herself
    # Append the valid entry and finally return it
    for i in userlog:
        index += 1
        listuser = i.split("; ")
        if user == listuser[2]:
            continue
        else:
            result += str(index) + i
    print('Return the active user list:\n' + result)
    return result


def out(user):
    global userlog
    global logseq
    index = 0

    # We need to find the user who wants to logout
    # Delete this entry
    for i in userlog:
        listuser = i.split("; ")
        if user == listuser[2]:
            del userlog[index]
            logseq -= 1
            break
        index += 1

    # After we find the user and delete the file
    # We need to update the userlog.txt
    f = open('userlog.txt', 'w')
    index = 0
    for i in userlog:
        index += 1
        f.write(str(index) + i)
    f.close()

# This is the main function
# We will have the socket, addr, and username as the argument
def recv_handler(con, addr, user):
    global userlog
    print('Server is ready for service')
    while (1):

        # Now we have passed the authentication part, we need to process the next command
        allcommand = client_sock.recv(2048).decode('utf-8')

        # The first three chars defines which function we need to call
        # All the command are separated using space
        command = allcommand[0:3]

        # For MSG, the rest is the only argument
        if command == 'MSG':
            info = allcommand[4::]
            msg(con, info, user)

        # For DLT, there is seq number, times, username
        elif command == 'DLT':
            info = allcommand[4::]
            info = info.split()
            seq = info[0]
            seq = seq.replace('#', '')
            times = ' '.join(info[1::])
            dlt(con, times, seq, user)

        # For EDT, it is similar to DLT. Except there is the new messagee
        elif command == 'EDT':
            info = allcommand[4::]
            info = info.split()
            seq = info[0]
            seq = seq.replace('#', '')
            times = ' '.join(info[1:5])
            msge = ' '.join(info[5::])
            edt(con, times, seq, user, msge)

        # For RDM, there is only the time stamp
        elif command == 'RDM':
            print(user + " issued RDM command.\n")
            times = allcommand[4::]
            returned = rdm(times)
            client_sock.send(returned.encode('utf-8'))
            print(returned)

        # ATU and OUT does not take argument
        elif command == 'ATU':
            print(user + ' issued ATU command.\n')
            info = atu(user)
            print(info+"\n")
            client_sock.send(info.encode('utf-8'))

        # The UPD function can have everthing it need by calling ATU
        elif command == 'UPD':
            info = allcommand[4::]

            # We need to find the user and if cannot find then send offline
            isoffline = 'Offline'
            for i in userlog:
                listuser = i.split("; ")
                if info == listuser[2]:
                    isoffline = listuser[3] + ' ' + listuser[4]
                    break
            client_sock.send(isoffline.encode('utf-8'))

        # This is the out command
        elif command == 'OUT':
            print(user + ' logged out\n')
            out(user)

            # Send an out message to the client
            client_sock.send('out'.encode('utf-8'))
            break

    client_sock.close()


# we will use two sockets, one for sending and one for receiving
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

serverSocket.bind(('127.0.0.1', serverPort))
serverSocket.listen(5)

# The main thread
while True:

    # Once a client enter, we record the socket and address and pass then to the authentication part
    # If they pass the authentication, we will have a username represent this client
    client_sock, client_addr = serverSocket.accept()
    user = authentication(client_sock, client_addr)

    # If the authentication passed, we start a new thread for the following command
    # If not, we close the socket
    if not user:
        client_sock.close()
    else:
        # Prevent timing out
        #serverSocket.setblocking(1)
        thread = threading.Thread(target=recv_handler, args=(client_sock, client_addr, user,))
        thread.start()