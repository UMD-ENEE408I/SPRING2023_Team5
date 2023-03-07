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
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"



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

# Plot wave file
# read audio samples
input_data = read("output.wav")
audio = input_data[1]

# plot the first 1024 samples
#plt.plot(audio)
# label the axes
#plt.ylabel("Amplitude")
#plt.xlabel("Time")
# set the title  
#plt.title("Output Wav")
# display the plot

#plt.plot(freq[1024])
#plt.show()

freq = fft(audio)
N = len(freq)
print(audio)
xf = fftfreq(N, 1 / RATE)
plt.plot(xf, np.abs(freq))
plt.show()
print('HERE')
data, rate = sf.read("output.wav")
meter = pyloudnorm.Meter(rate) #
loudness = meter.integrated_loudness(data)

print(loudness)
