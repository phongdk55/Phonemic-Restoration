import numpy as np
import os
from load_data_DNN import read_file_test, read_afile
from math import *

origin_dir = '/home/danglab/Phong/features/origin/input/'         #file includes 12-MFCC, 24-pos
#after_dnn_dir = '/home/danglab/Results/PhonemicRestoration/5_layers/origin/full_EMA/test_0/'
after_dnn_dir = '/home/danglab/Results/PhonemicRestoration/5_layers/space/SP_full_EMA/test_0/0_50ms_1_-6dB/'
#before_dnn_dir = '/home/danglab/Results/PhonemicRestoration/5_layers/origin/no_EMA/test_0/'
before_dnn_dir = '/home/danglab/Results/PhonemicRestoration/5_layers/space/SP_no_EMA/test_0/0_50ms_1_-6dB/'
#after_dnn_dir = '/home/danglab/Results/PhonemicRestoration/5_layers/space/artic_inter/test_0/10ms/'

def normalise_mfcc(X):
    max_X = abs(X).max()
    #print max_X                               
    Y = X / max_X
    return Y[:,1:13] 

def evaluate(original_file, test_file):    
    #print original_file
    #print test_file
    ori_arr, factors = read_file_test(original_file, 13, "factors")
    test_arr = read_file_test(test_file, 13)
    
    ori_arr = ori_arr[:,1:13] * factors #normalise_mfcc(ori_arr)               # take 12 coefficients
    #print ori_arr
    test_arr = test_arr[:,1:13]
    #print test_arr
    
    subtract = (ori_arr - test_arr) ** 2
    rms = sqrt(subtract.sum()) #/(ori_arr.shape[0] * ori_arr.shape[1])
    
    [m,n] = ori_arr.shape
    a = ori_arr.reshape(1,m*n)
    b = test_arr.reshape(1,m*n)
    return np.corrcoef(a,b)[0,1]
    
    return rms

def run():   
    total_rms = 0
    cnt = 0
    #find = folder.split('_')
    for filename in sorted(os.listdir(before_dnn_dir)):     #cac filename trong tung test    
        #break
        file_before_dnn =  before_dnn_dir  + filename       # file trc khi cho vao DNN
        a_rms = evaluate(origin_dir + filename.replace('.txt','_in.txt'), file_before_dnn)     
        total_rms += a_rms
        cnt +=1
    print 'No EMA: ', total_rms / cnt, cnt     
    
    
    total_rms = 0
    cnt = 0
    for filename in sorted(os.listdir(after_dnn_dir)):     #cac filename trong tung test
        #print filename
        file_after_dnn = after_dnn_dir + '/' +filename             # file sau khi cho vao DNN
        a_rms = evaluate(origin_dir + filename.replace('.txt','_in.txt'), file_after_dnn )
        total_rms += a_rms
        cnt +=1
    print 'Full EMA: ', total_rms / cnt, cnt
'''    

def run():
    list_folder = sorted(os.listdir(after_dnn_dir))
    for folder in list_folder:          # cac thu muc con
        
        directory_ = after_dnn_dir + folder
        print directory_
               
        total_rms = 0
        cnt = 0
        #find = folder.split('_')
        for filename in sorted(os.listdir(directory_)):     #cac filename trong tung test    
            #break
            file_before_dnn =  before_dnn_dir + folder + '/' + filename       # file trc khi cho vao DNN
            #try:
            a_rms = evaluate(origin_dir + filename.replace('.txt','_in.txt'), file_before_dnn)     
            total_rms += a_rms
            cnt +=1
            #except:
                #print filename
        print 'No EMA: ', total_rms / cnt, cnt     
        
        
        total_rms = 0
        cnt = 0
        for filename in sorted(os.listdir(directory_)):     #cac filename trong tung test    
            file_after_dnn = directory_ + '/' +filename             # file sau khi cho vao DNN
            a_rms = evaluate(origin_dir + filename.replace('.txt','_in.txt'), file_after_dnn )
            total_rms += a_rms
            cnt +=1
        print 'Full EMA: ', total_rms / cnt, cnt
'''
run()