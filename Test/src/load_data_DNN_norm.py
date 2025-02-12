import numpy as np
import os
import re
import math
from time import sleep

input_dir = "/home/danglab/Features/Input/input.txt"
output_dir = "/home/danglab/Features/Output/output.txt"

def read_data(filename, num_features, *arg):   
    input_file = open(filename,'r')
    feature = np.zeros((num_features))
    features_arr = []
    factor_arr = []
    
    count = 0
    for line in input_file:
        count += 1
        if count > 10000:
            break
        sequential_number = line.split(" ")
        if len(arg) > 0:
            start = 1
            factor_arr.append(float(sequential_number[0]))
        else:
            start = 0 
        for i in xrange(start, num_features):
            try:
                feature[i] = (float(sequential_number[i]))
            except:
                continue
        features_arr.append(feature)
        
    if len(arg) > 0:
        return np.array(features_arr).astype(np.float32), np.array(factor_arr).astype(np.float32)
    return np.array(features_arr).astype(np.float32)
    
def load_data():
    input_data = read_data(input_dir, 108)
    output_data, factor_data = read_data(output_dir, 36, "True")
    print input_data.shape, output_data.shape
    return input_data, output_data, factor_data

input_arr = []
output_arr = []
#test_arr = []
#test_res_arr = []
#factors = []

def read_afile(filename, num_features, arr):
    input_file = open(filename,'r')
    #print sum(1 for _ in input_file)
    for line in input_file:
        sequential_number = line.split(" ")
        feature = np.zeros((num_features))
        if len(sequential_number) > num_features: 
            for i in xrange(num_features):
                try:
                    if math.isnan(float(sequential_number[i])):
                        print line
                        print "AAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                        exit() 
                    feature[i] = (float(sequential_number[i]))                
                except:
                    print "Error --read-afile - check it"
            arr.append(feature)
            
def read_features():
    feature_in_dir = '/home/danglab/Phong/norm/input_norm/'
    feature_out_dir = '/home/danglab/Phong/norm/output_norm/'
    
    count = 0
    listfile = sorted(os.listdir(feature_in_dir))
    for afile in listfile:
        read_afile(feature_in_dir + afile,109 , input_arr)
        if count > 2:
            break
        count += 1      
              
    count = 0
    listfile_out = sorted(os.listdir(feature_out_dir))
    for afile in listfile_out:
        read_afile(feature_out_dir + afile, 13 + 24, output_arr)
        if count > 2:
            break
        count += 1

    return np.array(input_arr).astype(np.float32), np.array(output_arr).astype(np.float32)

#load_data()
#read_features()
