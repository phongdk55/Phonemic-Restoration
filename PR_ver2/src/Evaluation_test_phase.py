import numpy as np
import os
from load_data import read_file_test, read_afile
from math import *
from audioop import rms

origin_dir = '/home/danglab/Phong/features/origin/input/'

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
    [m,n] = ori_arr.shape
    #print m,n
    ori_arr = ori_arr[:,1:13] * factors #normalise_mfcc(ori_arr)               # take 12 coefficients
    test_arr = test_arr[:,1:13]
    
    subtract = (ori_arr - test_arr) ** 2
    #subtract = (ori_arr[2:m-3,:] - test_arr[2:m-3,:]) ** 2
    rms = sqrt(subtract.sum()) #/(ori_arr.shape[0] * ori_arr.shape[1])
    
    #print 
    #print ori_arr[m-3]
    #print test_arr[m-3]
    #print subtract[m-3]
    #exit()
    #a = ori_arr.reshape(1,m*n)
    #b = test_arr.reshape(1,m*n)
    #return np.corrcoef(a,b)[0,1]
    
    return rms

def test_1():   
    full_audio_ema = '/home/danglab/Results/PR_ver2/origin/full_EMA/test_0/'
    full_audio = '/home/danglab/Results/PR_ver2/origin/no_EMA/test_0/'

    print 'Full audio + full ema ', estimate(full_audio_ema)    
    print 'Full audio without ema ', estimate(full_audio)

def test_2():   
    space_audio = '/home/danglab/Results/PR_ver2/space/20ms/full_EMA/test_0/'    
    print 'Space audio + ema ', estimate(space_audio)
    
    space_audio_ema = '/home/danglab/Results/PR_ver2/space/20ms/no_EMA/test_0'
    print 'Space audio without ema', estimate(space_audio_ema)
    
def test_3():
    artic_interpolation = '/home/danglab/Results/PR_ver2/space/artic_inter/test_0/20ms/'
    print 'Space audio + inter_ema', estimate(artic_interpolation)
    
    space_interpolation = '/home/danglab/Results/PR_ver2/space/space_inter/test_0/20ms/'
    print 'inter space + inter ema ', estimate(space_interpolation) 
    
def estimate(path):
    total_rms = 0
    cnt = 0
    for filename in sorted(os.listdir(path)):     #cac filename trong tung test
        #print filename
        file_ = path + '/' +filename             # file sau khi cho vao DNN
        a_rms = evaluate(origin_dir + filename.replace('.txt','_in.txt'), file_ )
        #print a_rms
        total_rms += a_rms
        cnt +=1
    return total_rms/cnt, cnt

test_1()
test_2()
test_3()

'''
Full audio + full ema  (396.4406300659908, 36)
Full audio without ema  (398.94825797761905, 36)
Space audio + ema  (722.7486339659968, 36)
Space audio without ema (734.169364293101, 36)
Space audio + inter_ema (744.3050163295608, 36)
inter space + inter ema  (758.1265117606358, 36)
'''