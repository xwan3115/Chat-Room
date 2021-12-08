# Python version 3

# coding: utf-8
from socket import *
import sys, os
import time
from datetime import datetime

# So server name is localhost
# change port number if required; has to be larger than 1024
serverName = sys.argv[1]
serverPort = sys.argv[2]
serverPort = int(serverPort)

# Create the socket, after 600ms without any response considered loss
clientSocket = socket(AF_INET, SOCK_DGRAM)
timeout = 0.6
clientSocket.settimeout(timeout)

# The nb of pings we will send
nb_ping = 15

# Set max min avg for later use
minimum = 999
maximum = 0
avg = 0

# Record the successful ping to calculate average
success_ping = 0

# The sequence starts at 3331
seq_nb = 3331

# Send 15 pings to the server
for i in range(nb_ping):

    # Obtain the current time
    ctime = datetime.now().time()

    # The format of the message is PING sequence_number time CRLF
    message = 'PING %d %s \r\n' % (seq_nb, ctime)
    try:
        # We then send the packet to server, and record the time
        clientSocket.sendto(message, (serverName, serverPort))
        start = time.time()

        # We will receive data from server, and we record the time
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        end = time.time()

        # We can calculate the RRT in ms
        rtt = (end - start) * 1000

        # We also record the maximum and minimum rrt to print later
        if minimum>rtt:
            minimum = rtt
        if maximum<rtt:
            maximum = rtt
        avg += rtt
        success_ping += 1

        # Print the summary for this packet
        print("ping to 127.0.0.1, seq = %d, rtt = %0.1f ms"%(seq_nb, rtt))
        seq_nb += 1

    except:

        # If we did not get any response, print the summary
        # Then we will send the next packet
        print("ping to 127.0.0.1, seq = %d, time out"%seq_nb)
        seq_nb += 1
        continue

# Socket closes
clientSocket.close()

# Now we will print the min/max/avg rtt
print("Maximum RTT is: %0.1f ms"%maximum)
print("Minimum RTT is: %0.1f ms"%minimum)
avgTime = avg/success_ping
print("Average RTT is: %0.1f ms"%avgTime)
