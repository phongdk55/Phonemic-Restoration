from math import *
import numpy as np
import os
from random import *
import math

FOLD = 10
#get_all_filename()     # do not run this command twice during the experience

def chunks(list_data, gap):
    #print "gap"
    for i in xrange(0,len(list_data),gap):
        #print i
        yield list_data[i:i+gap]
        
def slide(FOLD, list_data):       # chia thanh nhieu tap du lieu de test, moi tap gom test + train
    Test_Train = []
    
    shuffle(list_data)        # tron cac tram theo thu tu ngau nhien
    #print list_data
    nTram = int(math.ceil(len(list_data) / FOLD))   # chia cac tram thanh n phan
    
    data = list(chunks(list_data, nTram))
    #print data
    for i in xrange(0,FOLD):
        data_test = data[i]
        data_train = list_data[:]     # copy
        for u in data_test:
            data_train.remove(u)  
            
        data_test = sorted(data_test)     
        data_train = sorted(data_train) 
        Test_Train.append((data_test,data_train))     # chia lam 2 phan, luu vao list
    return Test_Train

def get_all_filename():
    file_dir = '/home/danglab/Phong/norm/input_norm/'
    list_data = []
    
    for filename in os.listdir(file_dir):
        if filename.endswith('.txt'):
            list_data.append(filename) 
    print len(list_data)
    test_train = slide(FOLD,list_data)
    for u in xrange(FOLD):
        test = test_train[u]
        file_test = open('../Folds/test_train_' + str(u) + '.txt', 'w' )
        file_test.write("%s %s\n" %(len(test[0]), len(test[1])))
        for i in xrange(2):
            for k in xrange(len(test[i])):
                file_test.write('%s\n' %(test[i][k]))            

def rename_all_file():
    #direc = '/home/danglab/Phong/TestData/Features_Norm_Space/'
    direc = '/home/danglab/Phong/features_3p/Space/'
    for folder in os.listdir(direc):
        path = direc + folder + "/"
        for filename in os.listdir(path):
            print filename
            print filename.replace("_in_in",'_in')
            os.rename(path+filename, path + filename.replace("_in_in",'_in'))
#rename_all_file()          
