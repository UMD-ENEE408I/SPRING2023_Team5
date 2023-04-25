import socket 
import struct
import threading
import os
import time
import numpy as np

localIP = ''
localPort = 3333
localAny = "0.0.0.0"

global m1_address
global m2_address
global m1_port
global m2_port
global m1_theta
global m2_theta
global m1_en
global m2_en

m1_theta = 5
m2_theta = 10


msg = "10"

UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) #Creates UDP socket
UDPServerSocket.bind((localAny, localPort))

print("UDP server up and listening")

def get_address():
    counter = 0
    while counter < 1:
        (mice, address) = UDPServerSocket.recvfrom(1024)
        if mice.decode() == "mice1":
            m1_address = address[0]
            m1_port = address[1]
            #print('Mice 1 address: {}'.format(mice.decode()))
            UDPServerSocket.sendto(msg.encode(), (m1_address, m1_port))
            counter = counter + 1
            print('Mice 1 Connected!!!')

        elif mice.decode() == "mice2":
            m2_address = address[0]
            m2_port = address[1]
            UDPServerSocket.sendto(msg.encode(), (m2_address, m2_port))
            counter = counter + 1
            print('Mice 2 Connected!!!')


def send():
    while True:
        if m1_parity == 1: #After computing the theta, enable the condition and send theta value
            UDPServerSocket.sendto(m1_theta.encode(), m1_address)
            m1_parity = 0
        elif m2_parity == 1:
            UDPServerSocket.sendto(m2_theta.encode(), m2_address)
            m2_parity = 0

#def receive():
    #global m1_parity
    #global m2_parity
    while True:
        msg1 = UDPServerSocket.recvfrom(1024)
        if msg1[1] == m1_address:
            print(msg1[0].decode() + "\n")
            m1_parity = 1
        elif msg1[1] == m1_address:
            print(msg1[0].decode() + "\n")
            m2_parity = 1


x1 = threading.Thread(target = get_address)
#x2 = threading.Thread(target = send)
#x3 = threading.Thread(target = receive)

x1.start()
#time.sleep(3)
#x2.start()
#x3.start()