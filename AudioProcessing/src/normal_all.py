import theano
from theano import tensor as T
import numpy as np
from load_data_DNN import load_data, read_features
import math
import os,re
import logging
from weight_matrix import save_weight_info, load_weight_info, load_initial_info

def sgd(cost, params, lr=0.05):             # generalize to compute gradient descent
    grads = T.grad(cost=cost, wrt=params)   # on all model parameters
    updates = []
    for p, g in zip(params, grads):
        updates.append([p, p - g * lr])
    return updates

def model(X, params):         
    for u in xrange(len(params)-1):
        h = T.nnet.sigmoid(T.dot(X, params[u]))     # use tanh function        [0,1]
        X = h
    pyx = T.nnet.softmax(T.dot(X, params[len(params) - 1]))     # hidden -> output    [0.1]
    #pyx = h    
    return pyx

def read_file_test(filename, num_features, *args):
    input_file = open(filename,'r')
    feature = np.zeros((num_features))
    arr = []
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
    return np.array(arr).astype(np.float32)

def abs_normal_matrix(trX):
    mask = np.greater(trX,0)
    trX = np.choose(mask,(abs(trX), trX))
    #print trX
    #print mask
    max_X = trX.max()
    trX = trX / max_X
    return trX, mask, max_X

def deep_neural_network():
    trX, trY = read_features()        
    trX, mask, max_x = abs_normal_matrix(trX)
    for u in xrange(trX.shape[0]):
        trY[u] = np.concatenate((trX[u][0:13], trX[u][37:37+24]))
    
    #print trX.shape
    #print trY.shape
        
    X = T.fmatrix()
    Y = T.fmatrix()    
    load_params = True
    hidden_layer = '6_layers/'       # = n_hidden layer below
    artic = 'artic/'
    id_file = 0
    weight_folder = '../weight_DNN/' + hidden_layer + artic
    
    if not os.path.exists(weight_folder):
        os.makedirs(weight_folder)
        
    filename = weight_folder + 'Phonemic_DNN_SGD_id_' + str(id_file) + ".txt"
    
    if load_params:
        nloop,n_hidden_layer, n_input_f, n_hidden_f, n_output_f, params = load_weight_info(filename)             
    else:
        nloop = 0
        n_hidden_layer = 6
        n_input_f = 109
        n_hidden_f = 512 
        n_output_f = 37
        params = load_initial_info(n_hidden_layer, n_input_f, n_hidden_f, n_output_f)    
        
    trX = trX[:,1:n_input_f]
    print trX.max(), trX.min()
    trY = trY[:,1:n_output_f]
    print trY.max(), trY.min()
    #print trX.shape
    #print trY.shape
    print "trX"   
    #print trX
    print "trY"
    #print trY
    print nloop,n_hidden_layer, n_input_f, n_hidden_f, n_output_f
    
    py_x = model(X, params)
    y_x = py_x
    #cost = T.mean(T.nnet.categorical_crossentropy(py_x, Y))
    cost = T.mean(T.sqr(py_x - Y))
    #params = [w_h, w_h1, w_h2, w_h3, w_o]
    updates = sgd(cost, params)
    train = theano.function(inputs=[X, Y], outputs=cost, updates=updates, allow_input_downcast=True)
    predict = theano.function(inputs=[X], outputs=y_x, allow_input_downcast=True)
    
    LOG_FILENAME = 'DNN.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
          
    for i in range(nloop, nloop + 1):
        print i
        #logging.debug('loop' + str(i))
        error_total = 0
        arr_X_Y = zip(range(0, len(trX), 128), range(128, len(trX), 128))
        for start, end in arr_X_Y:
            cost = train(trX[start:end], trY[start:end])
            error_total += cost
            #print cost
        last_element = arr_X_Y[len(arr_X_Y)-1][0] 
        #logging.warning(str(params[n_hidden_layer - 1].get_value()))
        
        if last_element < len(trX):
            cost = train(trX[last_element: len(trX)], trY[last_element:len(trY)])    
            error_total += cost
        print error_total #/ len(trX)
        save_weight_info( filename, i, n_hidden_layer, n_input_f, n_hidden_f, n_output_f, params, error_total)
        id_file = 1 - id_file
        filename = weight_folder + 'Phonemic_DNN_SGD_id_' + str(id_file) + ".txt"
       
    #feature_out_dir = '/home/danglab/Phong/norm/output_norm/'
    test_dir = '/home/danglab/Phong/TestData/Features/minus/6dB/'
    dnn_predict_dir = '/home/danglab/DNN_Predict/normal_all/' + artic + 'minus/6dB/'
    
    if not os.path.exists(dnn_predict_dir):
        os.makedirs(dnn_predict_dir)
        
    listtest = sorted(os.listdir(test_dir))
    cnt = 0
    
    for afile in listtest:
        #print afile                 #usctimit_ema_f1_001_005_100ms_noise_in.txt
        test_arr = read_file_test(test_dir + afile, n_input_f, "factors")                                #read a missing_feature
        find_ = [m.start() for m in re.finditer('_', afile)]      
        file_mat = (afile.replace(afile[find_[4]:find_[6]],'')).replace('in.','out.')   #usctimit_ema_f1_001_005_out.txt
        #test_res_arr = read_file_test(feature_out_dir + file_mat, n_output_f)              #read an original output feature
        test_arr, mask, max_arr = abs_normal_matrix(test_arr)
        
        #print test_arr
        energy = test_arr[:,0]          #ko cho energy vao DNN
        test_arr = test_arr[:,1:n_input_f]
        
        #print "max_arr", max_arr
        write_predict_2_file(dnn_predict_dir + afile.replace(afile[find_[5]:find_[6]],'').replace("_out",''), energy, predict(test_arr), mask, max_arr)      # write result to file
        #break     
def write_predict_2_file(filename, energy, res_arr, mask, max_arr):
    files = open(filename, 'w')
    nframes = res_arr.shape[0]
    print res_arr
    mask_num = np.choose(mask, (-1,1))
    for i in xrange(nframes):
        files.write("%s "%(energy[i] * mask_num[i][0] *max_arr))        # restore energy
        for j in xrange(12):  #13
            files.write("%s " %(res_arr[i][j] * mask_num[i][j] * max_arr))
        files.write("\n")
    files.close()

deep_neural_network()