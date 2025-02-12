import numpy as np
import os
from math import *
#test 2: Sound wave with zero-fill intervals + articulatory data after interpolating the low-confidential interval
# = space audio (mfcc, del,del-del) + articulatory data interpolation

from load_data_DNN import read_file_test
artic_dir = '/home/danglab/Results/PhonemicRestoration/5_layers/space/SP_no_EMA/test_0/0_20ms_1_-3dB/'
artic_inter_dir = '/home/danglab/Results/artic_inter/20ms/' # articulatory_data
space_audio_dir = '/home/danglab/Phong/features/Space/0_20ms_1_-3dB/'

num_features = 49

def interpolate_10(position):
    m =  position.shape[0]
    position[0] = position[1]       # gap starts from 0,2,4..
    for i in xrange(2,m,2):
        try:
            position[i] = (position[i - 1] + position[i + 1]) / 2           #interpolate by averaging
        except:
            continue 
    #print position[:10,0]
    return position

def interpolate_20(position):
    m =  position.shape[0]
    position[0] = position[2]   # gap at 0-1, 4-5, 8-9...
    position[1] = position[3]
    print "20mmmmmmssssssssssssssss"
    for i in xrange(4,m,3):
        try:
            position[i] = (position[i - 1] + position[i + 1]) / 2           #interpolate by averaging
        except:
            continue 
    print position[:10,0]
    return position

def interpolate_50(position):
    print '50'
    
def get_position(filename):
    arr = read_file_test(filename, num_features)    #0:13, enegy+MFCC, 13:49, articulotory position    
    position = arr[:,13:13 + 12]        # position at i
    #print position.max(), position.min()
    if '10ms' in artic_dir:
        return interpolate_10(position)
    elif '20ms' in artic_dir:
        return interpolate_20(position)
    else:
        return interpolate_50(position)

def _deltas_calc(feature_data, w = 9):    #one dimension    # tu viet:P
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
    
    #http://docs.scipy.org/doc/numpy-1.10.0/reference/generated/numpy.convolve.html
    deltas = np.convolve(pad_data, win, 'valid') / (2 * factor)   # valid mean completely overlap  
    return deltas
        
def _get_velocity_acceleration(feature_data):
    m = feature_data.shape[0]
    velocity = np.zeros(feature_data.shape)
    acceleration = np.zeros(feature_data.shape)

    for organ in xrange(m):
        velocity[organ] = _deltas_calc(feature_data[organ])              #delta
        acceleration[organ] = _deltas_calc(velocity[organ])      #delta-delta
    return velocity, acceleration

def _stack_feature(raw_data):
    m,n =  raw_data.shape
    stacked_data = np.zeros((m,n*3))
    for u in xrange(m-2):
        stacked_data[u,:] = np.concatenate((raw_data[u,:], raw_data[u+1,:], raw_data[u+2,:]), axis =0)
    stacked_data[n-2,:] = np.concatenate((raw_data[n-2,:], raw_data[n-1,:], raw_data[n-1,:]), axis =0)      # separately processing the last two elements
    stacked_data[n-1,:] = np.concatenate((raw_data[n-1,:], raw_data[n-1,:], raw_data[n-1,:]), axis =0)
    return stacked_data

def write_features(filename, position, vec, acc, res_file):
    file_feature = open(res_file, 'w')    
    acoustic_feature, factors = read_file_test(filename, 37, "factor")     # energy , mfcc, del,del-del

    #mfcc = acoustic_feature[:,0:13]
    #delta = acoustic_feature[:,13:25]
    #delta_delta = acoustic_feature[:,25:37]
    min_nframes = min(acoustic_feature.shape[0],position.shape[0])
    #print min_nframes
    #list_feature = []
    file_feature.write('%s \n' %(factors))
    for fa in xrange(min_nframes):
        frame_feature = np.concatenate((acoustic_feature[fa,:],
                                        position[fa,:], vec[fa,:], acc[fa,:]), axis = 0)
        #print frame_feature.shape
        
        for i in frame_feature:
            file_feature.write("%s " %(i))
        file_feature.write("\n")
    file_feature.close()
    
def processing():
    if not os.path.exists(artic_inter_dir):
        os.makedirs(artic_inter_dir)
    list_file = sorted(os.listdir(artic_dir))
    for filename in list_file:
        print filename
        pos = get_position(artic_dir + filename)            # lay du lieu ket qua cua DNN
        vec, acc = _get_velocity_acceleration(pos)
        pos = _stack_feature(pos)
        vec = _stack_feature(vec)
        acc = _stack_feature(acc)
        #print acc.shape
        #print pos.max(), pos.min()
        #print vec.max(), vec.min()
        #print acc.max(), acc.min()  
        write_features(space_audio_dir + filename.replace(".txt", "_10ms_in.txt") , pos, vec, acc, artic_inter_dir + filename)      
        
        #break
    
processing()
'''
a = []
a.append(1)
a.append(2)
f = open('test.txt','w')
b = ['a','c','d']
print ", ".join(b)    
f.write(", ".join(b))
print str(a).strip('[]')
'''