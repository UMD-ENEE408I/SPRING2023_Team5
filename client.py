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

global CHUNK
global FORMAT
global CHANNELS
global RATE
global order
global cutoff
global speed
global RECORD_SECONDS
global THRESH
global test_val
global max_y
global keep_going
global WAVE_OUTPUT_FILENAME

localIP = ''
localPort = 3333
localAny = "0.0.0.0"
zeros = (0,0)
address = list(zeros) #Keeps track of respective robots ip address
port = list(zeros) #Keeps track of respective robots ip port
#theta = [0] * 2 #Keeps track of respective robots target_theta

#---------------------------------------- PYAUDIO CODE

order = 4
cutoff = (1300, 1600)
speed = 1.57
THRESH = 500
test_val = 0
max_y = 0
keep_going = True
#----------------------------------------

initialize = "5"

UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) #Creates UDP socket
UDPServerSocket.bind((localAny, localPort))

print("UDP server up and listening")

#-----------------------------------------------
				  
def get_address(mice):
	global address; global port
	(mice, addr) = UDPServerSocket.recvfrom(1024)
	while mice.decode() != "mice1":
		(mice, addr) = UDPServerSocket.recvfrom(1024)

	if mice.decode() == "mice1":
		mice = mice.decode()
		address[0] = addr[0]
		port[0] = addr[1]
		print('Mice 1 Connected!!!')
	elif mice.decode() == "mice2":
		mice = mice.decode()
		address[1] = addr[0]
		port[1] = addr[1]
		print('Mice 2 Connected!!!')

def send(theta, m_address, m_port):
	UDPServerSocket.sendto(theta.encode(), (m_address, m_port))

def receive(message):
	global address
	(message, address) = UDPServerSocket.recvfrom(1024)
	#if adr == address[0]:
	message = message.decode()
	#print("Mice 1: " + mssg + "\n")

def record():
	p = pyaudio.PyAudio()
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	# need to change to 2 for surface mic, 1 for wireless
	CHANNELS = 1
	RATE = 44100
	WAVE_OUTPUT_FILENAME = "output.wav"
	RECORD_SECONDS = 3

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

	test_val = max(audio_data);
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
	p = pyaudio.PyAudio()
	stream_real = p.open(format=FORMAT,
		channels=CHANNELS,
		rate=RATE,
		input=True,
		frames_per_buffer=CHUNK)
	stream_real.start_stream

	while keep_going:
		if(max_y >= THRESH): # Change threshold value here
			keep_going = False
			global fin_val
			fin_val = max_y
			print("\n")
			print(fin_val)
			print("\n")
		try:
			real_filt(stream_real.read(CHUNK))
			#y = butter_bandpass_filter(test_val, cutoff, RATE, order)
			#max_y = max(y)
			#print(max_y)
		except KeyboardInterrupt:
			keep_going=False
		except:
			pass
		
	#once the threshold is met then just quit I think? I don't think we need to keep that data, just tell bot to stop moving
	stream_real.stop_stream()
	stream_real.close()
	p.terminate()     

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
	global address; global port

	state = '0'
	msg = '0'
	receivee = '0'
	micee = 'm'
	msgg = '0'

	(micee, addr) = UDPServerSocket.recvfrom(1024)

	while receivee != "1" and micee != "mice1":
		while micee.decode() != "mice1":
			(micee, addr) = UDPServerSocket.recvfrom(1024)

		if micee.decode() == "mice1":
			micee = micee.decode()
			address[0] = addr[0]
			port[0] = addr[1]
			print('Mice 1 Connected!!!')


		#get_address(micee)
		send(initialize, address[0], port[0])
		receive(receivee)

		print("Receive:")
		print(receivee)
		print("MICE:")
		print(micee)

		if(receivee == "1" and micee == "mice1"):
			print("***STEP 1***")


	while msg != "1" and msgg != "5":
		send(state, address[0], port[0])
		receive(msg)
		send(initialize, address[0], port[0])
		receive(msgg)
		
		if msg == "1" and msgg == "5":
			print("***STEP 2***")
	
	print("***STEP 3***\n")

	sound_data = record()
	y = butter_bandpass_filter(sound_data, cutoff, RATE, order)
	theta = find_sound(y, RATE, speed)

	msg = "0"
	msgg = "0"
	while msg != "1" and msgg != "5":
		send(theta, address[0], port[0])
		receive(msg)
		send(initialize, address[0], port[0])
		receive(msgg)
		
		if msg == "1" and msgg == "5":
			print("***STEP 4***")


#x1 = threading.Thread(target = get_address)
#x2 = threading.Thread(target = send)
x3 = threading.Thread(target = locate)

#x1.start()
x3.start()