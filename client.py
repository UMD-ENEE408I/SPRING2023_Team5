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
localPort = 3333
localAny = "0.0.0.0"

global m1_address
global m2_address
global m1_port
global m2_port
global m1_theta
global m2_theta
global m1_sendtheta
global m2_sendtheta
global moving 

#---------------------------------------- PYAUDIO CODE
p = pyaudio.PyAudio()
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
global test_val
global max_y
global keep_going
global spin
start = "1"
target_v = "0"
spin = "1"
test_val = 0
max_y = 0
keep_going = True
#----------------------------------------

initialize = "1"

UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) #Creates UDP socket
UDPServerSocket.bind((localAny, localPort))

print("UDP server up and listening")

#-----------------------------------------------
stream_real = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True)#,
                    #frames_per_buffer=CHUNK)
#-----------------------------------------------
                  
def get_address():
    counter = 0
    while counter < 2:
        (mice, address) = UDPServerSocket.recvfrom(1024)
        if mice.decode() == "mice1":
            m1_address = address[0]
            m1_port = address[1]
            UDPServerSocket.sendto(initialize.encode(), (m1_address, m1_port))
            counter = counter + 1
            print('Mice 1 Connected!!!\n')

        elif mice.decode() == "mice2":
            m2_address = address[0]
            m2_port = address[1]
            UDPServerSocket.sendto(initialize.encode(), (m2_address, m2_port))
            counter = counter + 1
            print('Mice 2 Connected!!!')

def send(theta, m_address, m_port):
    UDPServerSocket.sendto(theta.encode(), (m_address, m_port))

def receive():
    while True:
        msg1 = UDPServerSocket.recvfrom(1024)
        if msg1[1] == m1_address:
            print(msg1[0].decode() + "\n")
        elif msg1[1] == m1_address:
            print(msg1[0].decode() + "\n")

def record():
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("*recording")

	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

	print("* done recording")

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
	b, a = butter_bandpass(cutoff, fs, order)
	y = filtfilt(b, a, data)
	test_val = max(y)
	return y

def real_filt(data): #reads and filters real time sound within bw
	
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
		
	stream_real.start_stream()

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
	if(spin == "1")
		send(spin, m1_address, m1_port)
		sound_data = record()
    	y = butter_bandpass_filter(sound_data, cutoff, RATE, order)
    	m1_theta = find_sound(y, RATE, speed)
    	send(m1_theta, m1_address, m1_port)
	elif(spin == "0")
		send(m1_theta, m1_address, m1_port)

	if(keep_going == False):
		send(target_v, m1_address, m1_port)
	elif(keep_going == True):
		realtime_sound()

x1 = threading.Thread(target = get_address)
x2 = threading.Thread(target = send)
x3 = threading.Thread(target = locate)

x1.start()
time.sleep(2)
x2.start()
x3.start()