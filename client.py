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
localAny = "0.0.0.0"
zeros = (0,0)
address = list(zeros) #Keeps track of respective robots ip address
port = list(zeros) #Keeps track of respective robots ip port
global theta  #Keeps track of respective robots target_theta
theta = 0.00
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
RECORD_SECONDS = 4
THRESH = 500
#global test_val
global max_y
#global keep_going
test_val = 0
max_y = 0
keep_going = True
#----------------------------------------
global state
initialize = "5"
state = 3
state_t = "1"

UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) #Creates UDP socket
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

#-----------------------------------------------

#-----------------------------------------------

				  
def get_address():
	global address; global port
	mice, addr = UDPServerSocket.recvfrom(1024)
	while mice.decode() != "3":
		mice, addr = UDPServerSocket.recvfrom(1024)

	if mice.decode() == "3":
		mice = mice.decode()
		address[0] = addr[0]
		port[0] = addr[1]
		#send(state, address[0], port[0])
		print('Mice 1 Connected!!!')		

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
	global address; global port; global theta
	global receiver; global state
	
	#get_address()

	while True:
		if state == 0: #Do nothing
			print("***State 0***")
		elif state == 1: #Spin Robot
			print("***State 1***")
			#send(state, address[0], port[0])
			sound_data = record()
			y = butter_bandpass_filter(sound_data, cutoff, RATE, order)
			theta = find_sound(y, RATE, speed)
			state = 2
		elif state == 2: #move robot
			print("***State 2***")
			i = 0
			for i in range(10):
				send(str(theta), address[0], port[0])
			state = 0
		elif state == 3: #initialize robot
			receiver, addr = UDPServerSocket.recvfrom(1024)
			print("***State 3***")
			address[0] = addr[0]
			port[0] = addr[1]
			send(state_t, address[0], port[0])
			print('Mice 1 Connected!!!')
			state = 1
		time.sleep(1.5)
locate()