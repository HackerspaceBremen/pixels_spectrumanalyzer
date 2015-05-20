import led
import sys
import pygame
from struct import unpack
import argparse
import csv
import fcntl
import gzip
import logging
import os
import random
from pygame.locals import *
import time
import alsaaudio as aa
import numpy as np

CHUNK_SIZE = 1024  # Use a multiple of 8

speed = 30

fallbackSize=(90, 20)

pygame.init()
pygame.display.set_mode()

fpsClock = pygame.time.Clock()

actual_columns=[0 for _ in range(90)]
columns=[0 for _ in range(90)]
c=0.0
decay=.7
def wheel_color(position):
    """Get color from wheel value (0 - 384)."""
    if position < 0:
        position = 0
    if position > 384:
        position = 384

    if position < 128:
        r = 127 - position % 128
        g = position % 128
        b = 0
    elif position < 256:
        g = 127 - position % 128
        b = position % 128
        r = 0
    else:
        b = 127 - position % 128
        r = position % 128
        g = 0

    return pygame.Color(r, g, b)



dsDisplay = led.dsclient.DisplayServerClientDisplay('localhost', 8123, fallbackSize)
simDisplay = led.sim.SimDisplay(dsDisplay.size())
pixelSurface = pygame.Surface(dsDisplay.size())
fftSurface = pygame.Surface(dsDisplay.size())
fftPixarray = pygame.PixelArray (fftSurface)
font = pygame.font.Font(None, 12)

def calculate_channel_frequency(min_frequency, max_frequency):
    '''Calculate frequency values for each channel, taking into account custom settings.'''

    # How many channels do we need to calculate the frequency for
    channel_length = 90
        
    logging.debug("Calculating frequencies for %d channels.", channel_length)
    octaves = (np.log(max_frequency / min_frequency)) / np.log(2)
    logging.debug("octaves in selected frequency range ... %s", octaves)
    octaves_per_channel = octaves / channel_length
    frequency_limits = []
    frequency_store = []
    
    frequency_limits.append(min_frequency)
    logging.debug("Custom channel frequencies are not being used")
    for i in range(1, 90 + 1):
        frequency_limits.append(frequency_limits[-1]*2**octaves_per_channel)
    for i in range(0, channel_length):
        frequency_store.append((frequency_limits[i], frequency_limits[i + 1]))
        logging.debug("channel %d is %6.2f to %6.2f ", i, frequency_limits[i],
                      frequency_limits[i + 1])

    return frequency_store

def piff(val, sample_rate):
    '''Return the power array index corresponding to a particular frequency.'''
    return int(CHUNK_SIZE * val / sample_rate)

def calculate_levels(data, sample_rate, frequency_limits):
    '''Calculate frequency response for each channel
....
    Initial FFT code inspired from the code posted here:
    http://www.raspberrypi.org/phpBB3/viewtopic.php?t=35838&p=454041
....
    Optimizations from work by Scott Driscoll:
    http://www.instructables.com/id/Raspberry-Pi-Spectrum-Analyzer-with-RGB-LED-Strip-/
    '''
    # create a numpy array. This won't work with a mono file, stereo only.
    data_stereo = np.fromstring(data[1], dtype=np.int16)
    
    data = np.empty(len(data[1]) / 4)  # data has two channels and 2 bytes per channel
    data[:] = data_stereo[::2]  # pull out the even values, just using left channel
    
    # if you take an FFT of a chunk of audio, the edges will look like
    # super high frequency cutoffs. Applying a window tapers the edges
    # of each end of the chunk down to zero.
    window = np.hanning(len(data))
    data = data * window
    
    fourier = np.fft.rfft(data)

    fourier = np.delete(fourier, len(fourier) - 1)
    
    power = np.abs(fourier) ** 2

    matrix = [0 for i in range(90)]
    for i in range(90):
        matrix[i] = np.log10(np.sum(power[piff(frequency_limits[i][0], sample_rate)
                                          :piff(frequency_limits[i][1], sample_rate):1]))

    return matrix


matrix = [0 for _ in range(90)]
offct = [0 for _ in range(90)]

def display_column(col=0,height=0.0,color=Color(50,50,0)):
        global c
        global columns
        global actual_columns
        global fftPixarray
        
        
        height = height - 9.0
        height = height / 5
        if height < .05:
                height = .05
        elif height > 1.0:
                height = 1.0
                
        if height < columns[col]:
                columns[col] = columns[col] * decay
                height = columns[col]
        else:
                columns[col] = height
        actual_columns[col]=int(round(height*20))
        c=int(round(col*4.26))
        color = wheel_color(int(c))
        if actual_columns[col] > 1:
            fftPixarray[col][19]=color
        else:
            fftPixarray[col][19]=Color(0,0,0)
        if actual_columns[col] > 2:
            fftPixarray[col][18]=color
        else:
            fftPixarray[col][18]=Color(0,0,0)
        if actual_columns[col] > 3:
            fftPixarray[col][17]=color
        else:
            fftPixarray[col][17]=Color(0,0,0)
        if actual_columns[col] > 4:
            fftPixarray[col][16]=color
        else:
            fftPixarray[col][16]=Color(0,0,0)
        if actual_columns[col] > 5:
            fftPixarray[col][15]=color
        else:
            fftPixarray[col][15]=Color(0,0,0)
        if actual_columns[col] > 6:
            fftPixarray[col][14]=color
        else:
            fftPixarray[col][14]=Color(0,0,0)
        if actual_columns[col] > 7:
            fftPixarray[col][13]=color
        else:
            fftPixarray[col][13]=Color(0,0,0)
        if actual_columns[col] > 8:
            fftPixarray[col][12]=color
        else:
            fftPixarray[col][12]=Color(0,0,0)
        if actual_columns[col] > 9:
            fftPixarray[col][11]=color
        else:
            fftPixarray[col][11]=Color(0,0,0)
        if actual_columns[col] > 10:
            fftPixarray[col][10]=color
        else:
            fftPixarray[col][10]=Color(0,0,0)

        if actual_columns[col] > 11:
            fftPixarray[col][9]=color
        else:
            fftPixarray[col][9]=Color(0,0,0)
        if actual_columns[col] > 12:
            fftPixarray[col][8]=color
        else:
            fftPixarray[col][8]=Color(0,0,0)
        if actual_columns[col] > 13:
            fftPixarray[col][7]=color
        else:
            fftPixarray[col][7]=Color(0,0,0)
        if actual_columns[col] > 14:
            fftPixarray[col][6]=color
        else:
            fftPixarray[col][6]=Color(0,0,0)
        if actual_columns[col] > 15:
            fftPixarray[col][5]=color
        else:
            fftPixarray[col][5]=Color(0,0,0)
        if actual_columns[col] > 16:
            fftPixarray[col][4]=color
        else:
            fftPixarray[col][4]=Color(0,0,0)
        if actual_columns[col] > 17:
            fftPixarray[col][3]=color
        else:
            fftPixarray[col][3]=Color(0,0,0)
        if actual_columns[col] > 18:
            fftPixarray[col][2]=color
        else:
            fftPixarray[col][2]=Color(0,0,0)
        if actual_columns[col] > 19:
            fftPixarray[col][1]=color
        else:
            fftPixarray[col][1]=Color(0,0,0)
        if actual_columns[col] > 20:
            fftPixarray[col][0]=color
        else:
            fftPixarray[col][0]=Color(0,0,0)


sample_rate=44100
num_channels=2
audio_input =aa.PCM(aa.PCM_CAPTURE,aa.PCM_NORMAL)
audio_input.setchannels(num_channels)
audio_input.setrate(sample_rate)
audio_input.setformat(aa.PCM_FORMAT_S16_LE)
audio_input.setperiodsize(CHUNK_SIZE)
mean = [12.0 for _ in range(90)]
std = [1.5 for _ in range(90)]
frequency_limits = calculate_channel_frequency(20,
                                               22000)


while True:
    data = audio_input.read()
    matrix = calculate_levels(data, sample_rate, frequency_limits)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pixelSurface.fill(pygame.Color(0, 0, 0))
    fftSurface.fill(pygame.Color(0, 0, 0))
    fps = font.render("FPS: {:.1f}".format(fpsClock.get_fps()), True, pygame.Color("#ff0000"))
    #pixelSurface.blit(fps, (0,0))
    for i in range(0, 89):
        display_column(i,matrix[i])
    
    pixelSurface.blit(fftPixarray.make_surface(), (0,0))
    
    
    
    
    dsDisplay.update(pixelSurface)
    simDisplay.update(pixelSurface)

    #fpsClock.tick(30)
