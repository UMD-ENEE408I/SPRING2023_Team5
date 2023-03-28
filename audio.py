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

p = pyaudio.PyAudio()
CHUNK = 1024
FORMAT = pyaudio.paInt16
# need to change to 2 for surface mic, 1 for wireless
CHANNELS = 1
RATE = 44100

WAVE_OUTPUT_FILENAME = "output.wav"
order = 6
cutoff = 3000
speed = 1.57
RECORD_SECONDS = 5

def record():
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

def freq_rsp(data): #takes time domain data and transforms to frequency domain
	freq = fft(data)
	return freq
	
def plot(data, choice):
	if(choice): #0 = time domain, 1 = freq domain
		plt.figure()
		N = len(data)
		xf = fftfreq(N, 1 / RATE)
		plt.plot(xf, np.abs(data))
		plt.ylabel("Amplitude")
		plt.xlabel("Frequency")
		
	else:
		plt.figure()
		#x_ax = len(data)/RATE
		plt.plot(data)
		plt.ylabel("Amplitude")
		plt.xlabel("Time")
		
		
def butter_lowpass(cutoff, fs, order):
    return butter(order, cutoff, btype='low', analog=False, output = 'ba', fs=fs)

def butter_lowpass_filter(data, cutoff, fs, order):
    b, a = butter_lowpass(cutoff, fs, order)
    y = filtfilt(b, a, data)
    return y

def find_sound(data, fs, speed):
	data_ls = data.tolist()
	max_v = max(data_ls)
	index = data_ls.index(max_v)
	print(index)
	time_max = float(index/fs)
	print(time_max)
	target_theta = speed*time_max
	print(target_theta)
	
	return target_theta
					
def main():
	samples = record()
	smp_freq = freq_rsp(samples)
	y = butter_lowpass_filter(samples, cutoff, RATE, order)
	y_freq = freq_rsp(y)
	
	target_v = find_sound(y, RATE, speed)
	
	plot(samples, 0)
	plot(smp_freq, 1)
	plot(y, 0)
	plot(y_freq, 1)v
	plt.show()

if __name__ == "__main__":
	main()
