import numpy as np
import os
from math import *
from interpolation import _get_velocity_acceleration, _stack_feature, normalise_unit

#test 2: Sound wave with zero-fill intervals + articulatory data after interpolating the low-confidential interval
# = space audio (mfcc, del,del-del) + articulatory data interpolation

from load_data import read_file_test
artic_dir = '/home/danglab/Results/PR_ver2/space/20ms/no_EMA/test_0/'
space_inter_dir = '/home/danglab/Results/space_inter/20ms/' # articulatory_data

num_features = 49
    
def get_data(filename):
    arr = read_file_test(filename, num_features)    #0:13, enegy+MFCC, 13:49, articulotory position    
    #position = arr[:,13:13 + 12]        # position at i
    return arr[:,0], arr[:,1:13], arr[:,13:13 + 12] 

def write_features(energy, factors, mfcc, delta, del_del, position, vec, acc, res_file):
    file_feature = open(res_file, 'w')    
    min_nframes = min(mfcc.shape[0],position.shape[0])
    file_feature.write('%s \n' %(factors))
    for fa in xrange(min_nframes):
        file_feature.write("%s " %(energy[fa]))
        frame_feature = np.concatenate((mfcc[fa,:], delta[fa,:], del_del[fa,:],
                                        position[fa,:], vec[fa,:], acc[fa,:]), axis = 0)
        for i in frame_feature:
            file_feature.write("%s " %(i))
        file_feature.write("\n")
    file_feature.close()

def interpolate_mfcc(mfcc):
    [m,n] =  mfcc.shape
    #print m,n
    arr = mfcc.copy()
    #print arr
    for i in xrange(3,m-2,4):       #3,7,11,...
        step = (arr[i+2] - arr[i]) / 3      # 3 doan bang nhau
        arr[i] = arr[i] + step
        arr[i+2] = arr[i+2] + step 
        arr[i+1] =  (arr[i] + arr[i+2]) / 2                
    return arr

def processing():
    if not os.path.exists(space_inter_dir):
        os.makedirs(space_inter_dir)
    list_file = sorted(os.listdir(artic_dir))
    for filename in list_file:
        print filename
        energy, mfcc, pos = get_data(artic_dir + filename)            # lay du lieu ket qua cua DNN
        print pos[2]
        mfcc = interpolate_mfcc(mfcc)
        factors = abs(mfcc).max()
        delta, del_del = _get_velocity_acceleration(mfcc)
        
        mfcc = normalise_unit(mfcc)
        delta = normalise_unit(delta)
        del_del = normalise_unit(del_del)
                       
        vec, acc = _get_velocity_acceleration(pos)
        #chuan hoa ve [-1,1]
        pos = _stack_feature(normalise_unit(pos))
        vec = _stack_feature(normalise_unit(vec))
        acc = _stack_feature(normalise_unit(acc))
        
        write_features(energy, factors, mfcc,delta, del_del, pos,vec, acc, space_inter_dir + filename)      

processing()