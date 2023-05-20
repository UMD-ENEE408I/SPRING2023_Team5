import socket 
import struct
import threading
import os
import time
import numpy as np
import pyaudio
import wave
import matplotlib.pyplot as plt
import sys
from scipy.io.wavfile import read
import soundfile as sf
import pyloudnorm
import scipy
from scipy.signal import butter, lfilter, freqz, filtfilt
from scipy.fft import fft, fftfreq
import socket 

localIP = ''
localPort = 8080
localAny = "172.20.10.2"
global theta  #Keeps track of respective robots target_theta
theta = 0.00
global receiver
receiver = b'0'
#---------------------------------------- PYAUDIO CODE

CHUNK = 1024
FORMAT = pyaudio.paInt16
# need to change to 2 for surface mic, 1 for wireless
CHANNELS = 1
RATE = 44100

WAVE_OUTPUT_FILENAME = "output.wav"
order = 4
cutoff = (1300, 1600)
speed = 1.57
RECORD_SECONDS = 1
THRESH = 500
#global test_val
global max_y
#global keep_going
test_val = 0
max_y = 0
keep_going = True
#----------------------------------------

initialize = "5"
state = "1"


UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDPServerSocket.bind((localAny, localPort))

UDPServerSocket.listen(1)

list_of_clients = []

print("UDP server up and listening")

#-----------------------------------------------

#-----------------------------------------------



				  
def get_address(conn, addr):
	while True:
			try:
				message = conn.recv(2048)
				if message:
					print ("<" + addr[0] + "> " + message)
 
					# Calls broadcast function to send message to all
					message_to_send = "<" + addr[0] + "> " + message
					broadcast(message_to_send, conn)
 
				else:
					remove(conn)
 
			except:
				continue		

def broadcast(message, connection):
	for clients in list_of_clients:
		if clients!=connection:
			try:
				clients.send(message)
			except:
				clients.close()
 
				# if the link is broken, we remove the client
				remove(clients)
 
def remove(connection):
	if connection in list_of_clients:
		list_of_clients.remove(connection)

def send(theta, m_address, m_port):
	UDPServerSocket.sendto(theta.encode(), (m_address, m_port))

def receive(message):
	global address
	message, address = UDPServerSocket.recvfrom(1024)
	#if adr == address[0]:
	message = message.decode()
	#print("Mice 1: " + mssg + "\n")

def record():
	global CHUNK; global FORMAT; global CHANNELS; global RATE
	global RECORD_SECONDS; global WAVE_OUTPUT_FILENAME
	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
	print("*recording")
	frames = []
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)
		 
	print("*done recording")
	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()
	input_data = read("output.wav")
	audio = input_data[1]
	return audio

def butter_bandpass(cutoff, fs, order): #function to initialize butterworth filter
	return butter(order, cutoff, btype='bandpass', analog=False, output = 'ba', fs=fs)

def butter_bandpass_filter(data, cutoff, fs, order):
	global test_val
	b, a = butter_bandpass(cutoff, fs, order)
	y = filtfilt(b, a, data)
	test_val = max(y)
	return y

def real_filt(data): #reads and filters real time sound within bw
	global max_y; global keep_going
	# get and convert the data to float
	audio_data = np.frombuffer(data, np.int16)

	test_val = max(audio_data)
	#print(test_val);

	y = butter_bandpass_filter(audio_data, cutoff, RATE, order)
	max_y = max(y)
	print(max_y)

	if keep_going:
		return True
	else:
		return False

def realtime_sound():
	global keep_going
	global CHUNK; global FORMAT; global CHANNELS; global RATE
	global RECORD_SECONDS
	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
	stream.start_stream()

	while keep_going:
		if(max_y >= THRESH): # Change threshold value here
			keep_going = False
			global fin_val
			fin_val = max_y
			print("\n")
			print(fin_val)
			print("\n")
		try:
			real_filt(stream.read(CHUNK))
			#y = butter_bandpass_filter(test_val, cutoff, RATE, order)
			#max_y = max(y)
			#print(max_y)
		except KeyboardInterrupt:
			keep_going=False
		except:
			pass
		
	#once the threshold is met then just quit I think? I don't think we need to keep that data, just tell bot to stop moving
	stream.stop_stream()
	stream.close()
	#p.terminate()

def find_sound(data, fs, speed):
	data_ls = data.tolist()
	print("total samples = ", len(data_ls))
	max_v = max(data_ls)
	print("max value = ", max_v)
	index = data_ls.index(max_v)
	print("index = ", index)
	time_max = float(index/fs)
	print("time_max = ", time_max)
	target_theta = speed*time_max
	print("target_theta = ", target_theta)
	
	return target_theta

def plot(data, choice):
	if(choice): #0 = time domain, 1 = freq domain
		plt.figure()
		N = len(data)
		freq = fft(data)
		xf = fftfreq(N, 1 / RATE)
		plt.plot(xf, np.abs(freq))
		plt.ylabel("Amplitude")
		plt.xlabel("Frequency")
		
	else:
		plt.figure()
		plt.plot(data)
		plt.ylabel("Amplitude")
		plt.xlabel("Time")

def locate():
	global theta
	global receiver
	while len(list_of_clients) != 1:
		conn, addr = UDPServerSocket.accept()
		list_of_clients.append(conn)

		print(addr[0] + " connected")

		#get_address(conn,addr)  
		

	while True:
		receiver = conn.recv(2048)
		print("Receiver")
		print(receiver.decode())
		if receiver.decode() == "0": #Do nothing
			print("***State 0***")
			
		elif receiver.decode() == "1": #Spin Robot
			broadcast(state, conn)
			print("***State 1***")
			
			sound_data = record()
			y = butter_bandpass_filter(sound_data, cutoff, RATE, order)
			theta = find_sound(y, RATE, speed)
			receiver = b'0'
		elif receiver.decode() == "2": #move robot
			print("***State 2***")
			broadcast(str(theta), conn)
			receiver = b'0'
		else:
			print("Do Nothing")

locate()
