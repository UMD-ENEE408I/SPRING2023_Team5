# HOW TO RECEIVE FILES FROM ONE PORT
# POSSIBLE WAY TO RECEIVE DEVICE LOCATION IN X,Y,Z COORDINATES AS A TXT FILE FROM OTHER ROBOTS AND DECODE

import socket 
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.0.142", 5656))
server.listen()

connection, address = server.accept()
print(f"[NEW CONNECTION] {address} connected.")
file_name = connection.recv(1024).decode()
print(f"[RECV] Receiving the filename.")
file = open("data.txt", "w")
data = connection.recv(1024).decode()
time.sleep(2)
connection.send("Filename received.".encode())
print(f"[RECV] Receiving the file data.")
file.write(data)
time.sleep(2)
connection.send("File data received".encode())
file.close()
connection.close()
print(f"[DISCONNECTED] {address} disconnected.")
