import numpy as np
import os
import re
import math

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

def read_afile(filename, num_features, arr ):
    input_file = open(filename,'r')    
    for line in input_file:
        sequential_number = line.split(" ")
        feature = np.zeros((num_features))
        if len(sequential_number) > num_features:
            for i in xrange(num_features):
                #print sequential_number[i]
                if math.isnan(float(sequential_number[i])):
                    print line
                    print "AAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                    exit() 
                try:
                    feature[i] = (float(sequential_number[i]))                
                except:
                    continue
            arr.append(feature)

def read_features():
    feature_in_dir = '/home/danglab/Phong/features/input/'
    feature_out_dir = '/home/danglab/Phong/features/output/'
    
    count = 0
    listfile = sorted(os.listdir(feature_in_dir))
    print len(listfile)
    listfile_out = sorted(os.listdir(feature_out_dir))
    print len(listfile_out)
    for afile in listfile:
        read_afile(feature_in_dir + afile,109 , input_arr)
        #print afile
#         if count > 10:
#             break
#         count += 1      
              
    count = 0
    
    for afile in listfile_out:
        read_afile(feature_out_dir + afile, 13 + 24, output_arr)
#         if count > 10:
#             break
#         count += 1
    
    return np.array(input_arr).astype(np.float32), np.array(output_arr).astype(np.float32)

#load_data()
#read_features()
