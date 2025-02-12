import numpy as np
#import struct
from wave import Wave_read
from matplotlib.pyplot import *
from scipy.io.wavfile import *
import scipy.io as sio
from features import * 
from math import floor
import matplotlib.pyplot as plt
import os

'''
file_wav_dir = "../Data/wav/"
file_mat_dir = "../Data/mat/"
filename = "usctimit_ema_f1_001_005"
'''

class AudioPreProcessing():
    def __init__(self, fileWav, fileMat, field, feature_out_dir):
        self.feature_out_dir = feature_out_dir
        self._readMatFile(fileMat, field)
        self._readAudioFile(fileWav)
        self._mat_pre_processing()
    
    def _readMatFile(self,fileMat, field):
        mat_dict = sio.loadmat(fileMat)
        #print mat_dict[0]
        mat_struct = mat_dict[field]
        size = mat_struct.shape      #truong 0: audio, truong 1->6 articulatory data: UL,LL,Jaw, TD, TB, TT
        name = []
        sr = np.zeros(size[1] - 1)     # sample rate of articulatory date
        
        for i in xrange(1,size[1]):     # organ i_th        # mang luu tu 0->5
            organ = mat_struct[0][i]
            name.append(organ[0][0])        # get name of an organ
            sr[i-1] = organ[1][0]           # get sample rate
            
            num_points = organ[2].shape[0]  # each point is a 3D point
            
            if i == 1:              # number of (organs*2) * number of sample points
                self.position = np.zeros(((size[1]-1) * 2,num_points))       # create a array : store 2-D forward-backward and up-down data, ignore side-to-side data 
            #print num_points
            for p in xrange(num_points):        #even : x-coordinate, odd: y-coordinate
                #position[i-1][p] = organ[2][p]
                self.position[(i-1) * 2][p] = organ[2][p][0]          # get 2-D points of an organ in time domain
                self.position[(i-1)*2 + 1][p] = organ[2][p][1]

    def _readAudioFile(self,fileWav):
        # http://stackoverflow.com/questions/2060628/how-to-read-wav-file-in-pythons
        wav_file = Wave_read(fileWav)
        self.nframes =  wav_file.getnframes()    
        sample_rate, wav_data = read(fileWav)
        self.duration = self.nframes / float(sample_rate)
        
        winlen = round(self.duration / self.position.shape[1], 6)       # winlen = length of articulatory frames
        mfcc_feat = mfcc(wav_data,sample_rate, 2* winlen, winlen)                  # need to define window length = ??, window step = ??
        #fbank_feat = logfbank(wav_data, sample_rate)
        #print fbank_feat[1:3,:]    
        #plt.plot(mfcc_feat)
        
        mfcc_feat =  np.transpose(mfcc_feat)
        self.mfcc_feature = mfcc_feat[1:13]
        
        self.factor_mfcc = abs(self.mfcc_feature).max()
        self.mfcc_feature = self.mfcc_feature / self.factor_mfcc            # normalize in [-1,1]
        
        veloc, accel = self._get_velocity_acceleration(self.mfcc_feature)
        self.velocity_mfcc = veloc
        self.acceleration_mfcc = accel
        #plt.plot(wav_data)
        #plt.show()
        #return mfcc_feat[1:13]      # get 12-coefficients from 1-12, except 0
        
    def _deltas_calc(self,feature_data, w = 9):    #one dimension    # tu viet:P
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
        
    def _get_velocity_acceleration(self,feature_data):
        m = feature_data.shape[0]
        velocity = np.zeros(feature_data.shape)
        acceleration = np.zeros(feature_data.shape)
    
        for organ in xrange(m):
            velocity[organ] = self._deltas_calc(feature_data[organ])              #delta
            acceleration[organ] = self._deltas_calc(velocity[organ])      #delta-delta
        return velocity, acceleration
        
    def _convert_2_z_scores(self,raw_data):
        m = raw_data.shape[0]
        z_scores_data = np.zeros(raw_data.shape)
        
        for organ in xrange(m):         #organ coordinate  even:x , odd:y
            mean_organ = np.mean(raw_data[organ])
            std_organ = np.std(raw_data[organ])
            #print mean_organ, std_organ
            z_scores_data[organ] = (raw_data[organ] - mean_organ) / std_organ        
        return z_scores_data
    
    def _stack_feature(self, raw_data):
        m,n =  raw_data.shape
        stacked_data = np.zeros((2*m,n))
        for u in xrange(n-1):
            stacked_data[:,u] = np.concatenate((raw_data[:,u], raw_data[:,u+1]), axis =0)
        return stacked_data
    
    def _mat_pre_processing(self):
        velocity, acceleration = self._get_velocity_acceleration(self.position)
        #conver to z_scores
        self._stack_feature(self.position)
        self.position = self._stack_feature(self._convert_2_z_scores(self.position))
        self.velocity_pos = self._stack_feature(self._convert_2_z_scores(velocity))
        self.acceleration_pos = self._stack_feature(self._convert_2_z_scores(acceleration))  
     
    def extract_feature(self):
        input_file = self.feature_out_dir + "Input/" + 'input.txt' 
        output_file = self.feature_out_dir + "Output/" + 'output.txt' 
#         file_feature = open(input_file, 'w')
#         file_mfcc_pos = open(output_file, 'w')
#         exit()
        if not os.path.exists(input_file):
            file_feature = open(input_file, 'w')        # 108 features for trainging data
        else:
            file_feature = open(input_file, 'a')
            
        if not os.path.exists(output_file):                 # 36 features for output of DNN
            file_mfcc_pos = open(output_file, 'w')
        else:
            file_mfcc_pos = open(output_file, 'a')
            
        min_nframes = min(self.mfcc_feature.shape[1],self.position.shape[1])
        print min_nframes
        #list_feature = []
        for fa in xrange(min_nframes):
            frame_feature = np.concatenate((self.mfcc_feature[:,fa], self.velocity_mfcc[:,fa], self.acceleration_mfcc[:,fa],
                                            self.position[:,fa], self.velocity_pos[:,fa], self.acceleration_pos[:,fa]), axis = 0)
            for i in frame_feature:
                file_feature.write("%s " %(i))
            file_feature.write("\n")
            
            mfpos_feature = np.concatenate(([self.factor_mfcc], self.mfcc_feature[:,fa], self.position[:,fa]), axis = 0)

            for i in mfpos_feature:
                file_mfcc_pos.write("%s " %(i))
            file_mfcc_pos.write("\n")
            
        file_feature.close()
        file_mfcc_pos.close()
        
if __name__ == "__main__":    
    ema_dir = "/home/danglab/kaldi-trunk/Data for DNN/EMA/Data/"
    feature_out_dir = "/home/danglab/Features/"
    
    for folder in os.listdir(ema_dir):
        #print folder
        list_file_wav = os.listdir(ema_dir + folder + "/wav/")
        list_file_wav = sorted(list_file_wav)
        for file_wav in list_file_wav:
            if file_wav.endswith(".wav"):                              
                #print file_wav,
                file_mat = ema_dir + folder + "/mat/" + file_wav.replace('.wav', '.mat')
                if os.path.exists(file_mat):
                    print file_mat
                    try:
                        au = AudioPreProcessing(ema_dir + folder + "/wav/"+ file_wav, file_mat, file_wav.replace('.wav', ''), feature_out_dir)
                        au.extract_feature()   
                    except:
                        #print "Error"
                        file_error = open("file_error", 'a')
                        file_error.write("%s\n" %file_mat)
                        file_error.close() 
        break