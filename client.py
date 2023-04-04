# HOW TO RECEIVE FILES FROM ONE PORT
# POSSIBLE WAY TO RECEIVE DEVICE LOCATION IN X,Y,Z COORDINATES AS A TXT FILE FROM OTHER ROBOTS AND DECODE

import socket 
import time

localIP = "192.168.2.10"
localPort = 3333

mice1_address = 1111
mice2_address = 2222
highIntensity1 = str.encode("Value of Intensity")
highIntensity2 = str.encode("Value of intensity")

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")
while(True):
    # If condition true, start receiving data
    #x = UDPServerSocket.recvfrom(xSize)
    #y = UDPServerSocket.recvfrom(ySize)
    #z = UDPServerSocket.recvfrom(zSize)
    #x_coordinate = x[0]
    # x_address = x[1]
    #y_coordinate = y[0]
    # x_address = y[1]
    #z_coordinate = z[0]
    # x_address = z[1]
    #address = bytesAddressPair[1]
    #clientMsg = "X Coordinate:{}".format(x_coordinate)
    #print(clientMsg)
    #clientMsg = "Y Coordinate:{}".format(y_coordinate)
    #print(clientMsg)
    #clientMsg = "Z Coordinate:{}".format(z_coordinate)
    #print(clientMsg)

    # Do computation to calculate V, theta, etc and send data back to robots motor
    UDPServerSocket.sendto(highIntensity1, mice1_address) #<--- Sends Data to mice 1
    UDPServerSocket.sendto(highIntensity2, mice2_address) #<--- Sends Data to mice 2
