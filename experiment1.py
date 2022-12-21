from scipy.io import wavfile as wav
from scipy.fftpack import fft
import pyaudio
import wave
import numpy as np
import time

from homeassistant_api import Client

with Client(
    'IP',
    'KEY'
) as client:

    light = client.get_domain("light")

    light.turn_on(entity_id="light.desk_light")



def isNumberInArray(array, number):
    offset = 5
    for i in range(number - offset, number + offset):
        if i in array:
            return True
    return False

DTMF_TABLE = {
    '1': [1209, 697],
    '2': [1336, 697],
    '3': [1477, 697],
    'A': [1633, 697],

    '4': [1209, 770],
    '5': [1336, 770],
    '6': [1477, 770],
    'B': [1633, 770],

    '7': [1209, 852],
    '8': [1336, 852],
    '9': [1477, 852],
    'C': [1633, 852],

    '*': [1209, 941],
    '0': [1336, 941],
    '#': [1477, 941],
    'D': [1633, 941],
} 

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 20000
CHUNK = 1024
RECORD_SECONDS = 0.4
WAVE_OUTPUT_FILENAME = "file.wav"
 
audio = pyaudio.PyAudio()
 
while (True):
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    rate, data = wav.read('file.wav')

    FourierTransformOfData = np.fft.fft(data, 20000)

    for i in range(len(FourierTransformOfData)):
        FourierTransformOfData[i] = int(np.absolute(FourierTransformOfData[i]))

    LowerBound = 20 * np.average(FourierTransformOfData)

    FilteredFrequencies = []
    for i in range(len(FourierTransformOfData)):
        if (FourierTransformOfData[i] > LowerBound):
            FilteredFrequencies.append(i)

    for char, frequency_pair in DTMF_TABLE.items():
        if (isNumberInArray(FilteredFrequencies, frequency_pair[0]) and
            isNumberInArray(FilteredFrequencies, frequency_pair[1])):
            print (char)
            RADIOCODE = char

            if RADIOCODE == "1":
                light.turn_on(entity_id="light.desk_light")
            elif RADIOCODE == "2":
                light.turn_off(entity_id="light.desk_light")
                
            elif RADIOCODE == "3":
                light.turn_on(entity_id="light.desk_light")
                time.sleep(0.5)
                light.turn_off(entity_id="light.desk_light")

            elif RADIOCODE == "9":
                light.turn_off(entity_id="light.desk_light")
                light.turn_off(entity_id="light.desk_light_2")
            
audio.terminate()
# nika was here
