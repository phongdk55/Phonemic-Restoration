import numpy as np
import os
from load_data_DNN import read_file_test, read_afile
from math import *

#origin_dir = '/home/danglab/Phong/features_3p/Noise/'
origin_dir = '/home/danglab/Phong/features_3p/origin/input/'         #file includes 12-MFCC, 24-pos
after_dnn_dir = '/home/danglab/3P/Net_Space/5_layers/100ms/artic/space/test_0/'
#after_dnn_dir = '/home/danglab/3P/Net_Space/unnormal/5_layers/100ms/artic/noises/test_0/'
before_dnn_dir = '/home/danglab/Phong/features_3p/Space/'

def normalise_mfcc(X):
    max_X = abs(X).max()
    #print max_X
    Y = X / max_X
    return Y[:,1:13] 

def evaluate(original_file, test_file):    
    ori_arr = read_file_test(original_file, 13, )
    test_arr = read_file_test(test_file, 13)
    ori_energy = ori_arr[:,0]
    test_energy = test_arr[:,0]
    
    ori_arr = ori_arr[:,1:13]#normalise_mfcc(ori_arr)               # take 12 coefficients
    test_arr = test_arr[:,1:13]
    #test_arr = normalise_mfcc(test_arr)
    #print test_arr.max()
    subtract = (ori_arr - test_arr) ** 2
    rms = sqrt(subtract.sum()) #/(ori_arr.shape[0] * ori_arr.shape[1])
    #print rms #, ori_arr.shape[0] * ori_arr.shape[1]
    #subtract = (ori_arr - test_arr)
    #print subtract.max()
    
    [m,n] = ori_arr.shape
    a = ori_arr.reshape(1,m*n)
    b = test_arr.reshape(1,m*n)
    #print a
    #print b
    #print np.corrcoef(a,b)[0,1]
    return np.corrcoef(a,b)[0,1]
    
    return rms

def run():
    list_folder = sorted(os.listdir(after_dnn_dir))
    for folder in list_folder:          # cac thu muc con
        
        directory_ = after_dnn_dir + folder
        print directory_
               
        total_rms = 0
        cnt = 0
        find = folder.split('_')
        for filename in sorted(os.listdir(directory_)):     #cac filename trong tung test    
            file_before_dnn =  before_dnn_dir + folder + '/' +filename.replace('.txt','_' + find[1] + "_in.txt")        # file trc khi cho vao DNN
            #try:
            a_rms = evaluate(origin_dir + filename.replace('.txt','_in.txt'), file_before_dnn)     
            total_rms += a_rms
            cnt +=1
            #except:
                #print filename
        print 'Before DNN: ', total_rms / cnt,     
        
        
        total_rms = 0
        cnt = 0
        for filename in sorted(os.listdir(directory_)):     #cac filename trong tung test    
            file_after_dnn = directory_ + '/' +filename             # file sau khi cho vao DNN
            a_rms = evaluate(origin_dir + filename.replace('.txt','_in.txt'), file_after_dnn )
            total_rms += a_rms
            cnt +=1
        print 'After: ', total_rms / cnt
run()
'''
/home/danglab/3P/Net_Noise/5_layers/SQR/artic/noises/test_0/0_100ms_1_-3dB
Before DNN:  0.403738200029 After:  0.69170427684
/home/danglab/3P/Net_Noise/5_layers/SQR/artic/noises/test_0/0_100ms_1_-6dB
Before DNN:  0.403738200029 After:  0.715031896825
/home/danglab/3P/Net_Noise/5_layers/SQR/artic/noises/test_0/0_200ms_1_-3dB
Before DNN:  0.399298414628 After:  0.61824315621
/home/danglab/3P/Net_Noise/5_layers/SQR/artic/noises/test_0/0_200ms_1_-6dB
Before DNN:  0.399298414628 After:  0.64394238071
/home/danglab/3P/Net_Noise/5_layers/SQR/artic/noises/test_0/0_50ms_1_-3dB
Before DNN:  0.416034360179 After:  0.698720745074
/home/danglab/3P/Net_Noise/5_layers/SQR/artic/noises/test_0/0_50ms_1_-6dB
Before DNN:  0.416034360179 After:  0.719566640897

'''
