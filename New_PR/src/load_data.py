import numpy as np
import os
import re
import math
from time import sleep

input_arr = []
output_arr = []
missing_filename = []

def read_afile(filename, num_features, arr):
    input_file = open(filename,'r')
    #print sum(1 for _ in input_file)
    for line in input_file:
        sequential_number = line.split(" ")
        feature = np.zeros((num_features))
        #print num_features
        #print len(sequential_number)
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

def read_features(test_number, n_input, n_output):
    feature_in_dir = '/home/danglab/Phong/features/origin/input/'
    feature_out_dir = '/home/danglab/Phong/features/origin/output/'
        
    file_test = open('../Folds/test_train_' + str(test_number) + '.txt','r')
    for line in file_test:
        split_number = line.split()
        number_test, number_train = int(split_number[0]), int(split_number[1])
        print number_test, number_train
        break       #phai co break o day
    
    count = 1
    for line in file_test:  # data test
        if count > number_test: 
            break
        filename = line.split()[0]
        missing_filename.append(filename.replace('_in.txt', ''))
        count +=1
    print 'length of testing data ', len(missing_filename)  
    for line in file_test:  # data train
        filename = line.split()[0]
                      
        input_file = feature_in_dir + filename
        output_file = feature_out_dir + filename.replace('in.','out.')
        read_afile( input_file,n_input , input_arr)
        read_afile(output_file, n_output, output_arr)  
        
        #break    
    print 'length of training data ', len(input_arr)
    return np.array(input_arr).astype(np.float32), np.array(output_arr).astype(np.float32), missing_filename

def read_file_test(filename, num_features, *args):
    input_file = open(filename,'r')
    feature = np.zeros((num_features))
    arr = []
    factors = 0
    flag = True
    for line in input_file:
        sequential_number = line.split(" ")
        feature = np.zeros((num_features))
        if flag:
            if len(args) > 0:           # line with a number of factor
                try:
                    factors = float(sequential_number[0])           #load factor, 0: MFCC factor, 1:del, 2:del, 3:p, 4:v,5:a 
                    flag = False
                    continue
                except:
                    print 'Unable to convert'
        
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
    if len(args) > 0: 
        return np.array(arr).astype(np.float32), factors
    return np.array(arr).astype(np.float32)


#load_data()
#read_features()
