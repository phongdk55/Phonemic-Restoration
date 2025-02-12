import numpy as np
import os
from load_data_DNN_norm import read_file_test, read_afile
from math import *

origin_dir = '/home/danglab/Phong/features/input/'         #file includes 12-MFCC, 24-pos
test_dir = '/home/danglab/DNN_Predict/Features_Norm/5_layers/SQR/artic/noises/test_0/'
#test_dir = '/home/danglab/Phong/TestData/Features_Norm/'
evaluation = ''

def evaluate(original_file, test_file):    
    ori_arr = read_file_test(original_file, 13, )
    test_arr = read_file_test(test_file, 13)
    ori_arr = ori_arr[:,1:13]               # take 12 coefficients
    test_arr = test_arr[:,1:13]
    
    subtract = (ori_arr - test_arr) ** 2
    rms = sqrt(subtract.sum()) #/(ori_arr.shape[0] * ori_arr.shape[1])
    print rms #, ori_arr.shape[0] * ori_arr.shape[1]
    #subtract = (ori_arr - test_arr)
    print subtract.max()
    return rms

def run():
    list_folder = sorted(os.listdir(test_dir))
    for folder in list_folder:
        directory_ = test_dir + folder
        print directory_
        for filename in sorted(os.listdir(directory_)):
            print filename
            #print filename.replace('.txt','_in.txt')
            evaluate(origin_dir + filename.replace('.txt','_in.txt'), directory_ + '/' +filename)
            #evaluate(origin_dir + filename.replace('_100ms',''), directory_ + '/' +filename)0            
            exit()
run()
