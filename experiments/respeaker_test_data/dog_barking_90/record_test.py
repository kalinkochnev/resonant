import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import wave
import math
import scipy.io.wavfile

FORMAT = pyaudio.paInt16
CHANNELS = 4
RATE = 348000
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "combined.wav"
 
audio = pyaudio.PyAudio()
 
# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
print ("recording...")
frames = []
 
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
frames = b''.join(frames)
print ("finished recording")
 
 
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(frames)
waveFile.close()

amplitude = np.frombuffer(frames, np.int16)
sig1 = amplitude[::4]
sig2 = amplitude[1::4]
sig3 = amplitude[2::4]
sig4 = amplitude[3::4]

fig = plt.figure()
s = fig.add_subplot(111)
s.plot(sig1)
fig.savefig('mic1.png')
scipy.io.wavfile.write("mic1.wav", RATE, np.array(sig1).astype(np.int16))

fig2 = plt.figure()
s2 = fig2.add_subplot(111)
s2.plot(sig2)
fig2.savefig('mic2.png')
scipy.io.wavfile.write("mic2.wav", RATE, np.array(sig2).astype(np.int16))

fig3 = plt.figure()
s3 = fig3.add_subplot(111)
s3.plot(sig3)
fig3.savefig('mic3.png')
scipy.io.wavfile.write("mic3.wav", RATE, np.array(sig3).astype(np.int16))

fig4 = plt.figure()
s4 = fig4.add_subplot(111)
s4.plot(sig4)
fig4.savefig('mic4.png')
scipy.io.wavfile.write("mic4.wav", RATE, np.array(sig4).astype(np.int16))
