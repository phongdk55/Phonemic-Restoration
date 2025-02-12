import numpy as np
#import struct
from wave import Wave_read
from matplotlib.pyplot import *
from scipy.io.wavfile import *
import scipy.io as sio
from features import * 
from math import floor
import matplotlib.pyplot as plt
#from scikits.talkbox.features import mfcc

file_wav_dir = "../Data/wav/"
file_mat_dir = "../Data/mat/"
filename = "usctimit_ema_f1_001_005"

def readAudioFile(fileWav):
    # http://stackoverflow.com/questions/2060628/how-to-read-wav-file-in-pythons
    wav_file = Wave_read(file_wav_dir + fileWav + ".wav")
    nframes =  wav_file.getnframes()    
    sample_rate, wav_data = read(file_wav_dir + fileWav + ".wav")
    mfcc_feat, mspec, spec = mfcc(wav_data,fs = sample_rate)
    print mfcc_feat.shape
    #fbank_feat = logfbank(wav_data, sample_rate)
    #print fbank_feat[1:3,:]    
    
    plt.imshow(mfcc_feat.T,aspect='auto')
    plt.colorbar()
    plt.show()
    
    mfcc_feat =  np.transpose(mfcc_feat)
    print mfcc_feat[0,:].shape
    v1 = deltas_calc(mfcc_feat[0,:])
    print v1
    
def deltas_calc(feature_data, w = 9):    #one dimension    # tu viet:P
    hlen = int(floor(w/2))
    w = 2 * hlen + 1
    
    #http://docs.scipy.org/doc/numpy-1.10.0/reference/generated/numpy.pad.html
    pad_data = np.lib.pad(feature_data, (hlen,hlen), 'edge')        # pad 2 sides of an array, each size hlen elements
    win = np.zeros((w))
    for u in xrange(1, hlen+1):
        win[hlen - u] = -u
        win[hlen + u] = u
    #print 'win ', win
    factor = hlen * (hlen + 1) * (2*hlen + 1) / 6  #sum of n^2
    
    print pad_data
    #http://docs.scipy.org/doc/numpy-1.10.0/reference/generated/numpy.convolve.html
    deltas = np.convolve(pad_data, win, 'valid') / (2 * factor)   # valid mean completely overlap  
    return deltas


def readMatFile(fileMat):
    mat_dict = sio.loadmat(file_mat_dir + fileMat)
    #print mat_dict[0]
    mat_struct = mat_dict['usctimit_ema_f1_001_005']
    size = mat_struct.shape      #truong 0: audio, truong 1->6 articulatory data: UL,LL,Jaw, TD, TB, TT
    name = []
    sr = np.zeros(size[1] - 1)     # sample rate of articulatory date
    
    for i in xrange(1,size[1]):     # organ i_th        # mang luu tu 0->5
        organ = mat_struct[0][i]
        name.append(organ[0][0])        # get name of an organ
        sr[i-1] = organ[1][0]           # get sample rate
        
        num_points = organ[2].shape[0]  # each point is a 3D point
        
        if i == 1:              # number of organs * number of sample points * 2 dimensions
            position = np.zeros((size[1]-1,num_points,2))       # create a array : store 2-D forward-backward and up-down data, ignore side-to-side data 
        #print num_points
        for p in xrange(num_points):
            #position[i-1][p] = organ[2][p]
            position[i-1][p][0] = organ[2][p][0]          # get 2-D points of an organ in time domain
            position[i-1][p][1] = organ[2][p][1]
    print position[0]
    get_velocity_acceleration_position(position)
    #convert_2_z_scores(position)
   
def get_velocity_acceleration_position(position):
    m = position.shape[0]
    for organ in xrange(m):
        #print position[0][:,0]
        velocity = deltas_calc(position[organ][:,0])
        break    
    
def convert_2_z_scores(raw_data):
    m = raw_data.shape[0]
    z_scores_data = np.zeros(raw_data.shape)
    
    for organ in xrange(m):
        mean_organ = np.mean(raw_data[organ],0)
        std_organ = np.std(raw_data[organ],0)
        #print mean_organ, std_organ
        z_scores_data[organ] = (raw_data[organ] - mean_organ) / std_organ        
    
    #print z_scores_data
    return z_scores_data


readAudioFile(filename)
#readMatFile(filename)
