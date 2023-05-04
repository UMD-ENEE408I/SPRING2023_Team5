import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
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
global self

order = 4
cutoff = (1300, 1600)
speed = 1.57
test_val = 0
max_y = 0
keep_going = True
THRESH = 500
	
def __init(self):
	self.audioGate = Event()
	self.audioGate.set()

def record(): #YOU NEED TO EDIT THIS TO RECORD WITH TWO MICS
	p = pyaudio.PyAudio()
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	# need to change to 2 for surface mic, 1 for wireless
	CHANNELS = 1
	RATE = 44100
	WAVE_OUTPUT_FILENAME = "output.wav"
	RECORD_SECONDS = 3
	

	stream = p.open(format=FORMAT,
		channels=CHANNELS,
		rate=RATE,
		input=True,
		frames_per_buffer=CHUNK)
	
	print("* recording")

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
	
def server_start(data):
	localIP = "192.168.2.10"
	localPort = 3333

	mice1_address = 1111
	#mice2_address = 2222
	highIntensity1 = str.encode("data") #we only need to do this if the data is a string, integers can be a string so this is probably the best way
	UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	UDPServerSocket.bind((localIP, localPort))
	
	print("UDP server up and listening")
	while(True):
		UDPServerSocket.sendto(highIntensity1, mice1_address) #<--- Sends Data to mice 1
		break
		
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
		
#def camera():
	#this should definitely all be in a header file to use the camera and openCV
	#will read the april tags and their distances to determine if they were moving when they take the measurement or whatever
							
def main():
	##START
	#server_start() #Im sure this will have to change
	#field_init() #camera using april tags to initialize playing field
	
	#might want to do the msg2client in each function and not in main

	while(1):
		#msg2client("3 green") #Tell bot 3 to make sound for green
		#msg2client("1 2 spin")
		sound_data = record()
		
		plot(sound_data, 0)
		
		print("end\n")
		break
		#y = butter_bandpass_filter(sound_data, cutoff, RATE, order) #passes time domain data through butter bp filter, returns filtered t data
		#target_theta = find_sound(y, RATE, speed) #uses time domain data to find the sound source and calculate target_theta of source
		#msg2client("1 2 theta") #this will trigger the bot to turn that way and to start moving
		#realtime_sound()
		#msg2client("1 2 stop")
		#camera() #did the camera catch the bots moving?? 
		
		
		
		
	#plot(samples, 0)
	#plot(samples, 1)
	#plot(y, 0)
	#plot(y, 1)
	plt.show()

if __name__ == "__main__":
	main()