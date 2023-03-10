import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.io.wavfile import read
import soundfile as sf
import pyloudnorm
import scipy
from scipy.fft import fft, fftfreq

p = pyaudio.PyAudio()
CHUNK = 1024
FORMAT = pyaudio.paInt16
# need to change to 2 for surface mic, 1 for wireless
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 15
WAVE_OUTPUT_FILENAME = "output.wav"

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
		N = len(data)
		xf = fftfreq(N, 1 / RATE)
		plt.plot(xf, np.abs(data))
		plt.ylabel("Amplitude")
		plt.xlabel("Frequency")
		plt.show()
	else:
		plt.plot(data)
		plt.ylabel("Amplitude")
		plt.xlabel("Time")
		plt.show()
				
def main():
	samples = record()
	smp_freq = freq_rsp(samples)
	plot(samples, 0)
	plot(smp_freq, 1)

if __name__ == "__main__":
	main()
