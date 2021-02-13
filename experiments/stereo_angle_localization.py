import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import wave
import math

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 384000 # in hertz
CHUNK = 1024
RECORD_SECONDS = 2
MIC_SEPARATION = 0.089 # in meters
SPEED_OF_SOUND = 343.0 # in meters/second

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

# save wav file
waveFile = wave.open("audio.wav", 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(frames)
waveFile.close()

# get amplitude arrays
amplitude = np.frombuffer(frames, np.int16)
leftStream = amplitude[1::2]
rightStream = amplitude[::2]

# plot the left and right audio streams
fig = plt.figure()
s = fig.add_subplot(111)
s.plot(rightStream)
fig.savefig('right.png')

fig2 = plt.figure()
s2 = fig2.add_subplot(111)
s2.plot(leftStream)
fig2.savefig('left.png')

# find the point of maximum correlation
# we keep one of the left stream as-is while offsetting the right stream by some number of indices
indicesToCheck = math.ceil((MIC_SEPARATION / SPEED_OF_SOUND) * RATE * 1.1) # we multiply by 1.1 as a safety factor
maxCorr = -999999
maxCorrIndex = -999999
correlationValues = []
for i in range(-indicesToCheck, indicesToCheck):
    thisCorr = np.corrcoef(leftStream, np.roll(rightStream, i), 'valid')[0][1]
    correlationValues.append(thisCorr)
    if (thisCorr > maxCorr):
        maxCorr = thisCorr
        maxCorrIndex = i

# plot the correlation values
fig5 = plt.figure()
s5 = fig5.add_subplot(111)
s5.plot(range(-indicesToCheck, indicesToCheck), correlationValues)
fig5.savefig('correlation-values.png')

# compute and print angle
x = (-maxCorrIndex / RATE * SPEED_OF_SOUND) / MIC_SEPARATION
print (maxCorrIndex, x)
if(x > 1):
    print(0)
elif(x < -1):
    print(180)
else:
    angle = math.acos(x)*(180/math.pi)
    print(angle)
