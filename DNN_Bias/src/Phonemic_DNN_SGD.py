import theano
from theano import tensor as T
import numpy as np
from load_data_DNN_norm import load_data, read_features
import math
import os,re
import logging
from weight_matrix import save_weight_info, load_weight_info, load_initial_info
#import matplotlib.pyplot as plt

def sgd(cost, params, bias, lr=0.05):             # generalize to compute gradient descent
    updates = []
    
    grads = T.grad(cost=cost, wrt=params)   # on all model parameters
    for p, g in zip(params, grads):
        updates.append([p, p - g * lr])
     
    grads = T.grad(cost=cost,wrt=bias)
    for p, g in zip(bias, grads):
        updates.append([p, p - g * lr])
    
    return updates

def model(X, params, bias):            # bias kich thuoc 1 * m, chi chay duoc voi tung frame, ko chay duoc vs nhieu frame 1 luc
    for u in xrange(len(params) - 1):
        h = T.tanh(T.dot(X, params[u]) + bias[u])    # use tanh function
        X = h
    pyx = T.dot(X, params[len(params) - 1]) + bias[len(params)-1]     # hidden -> output   
    
    return pyx

# def model(X, params, bias):         
#     for u in xrange(len(params) - 1):
#         h = T.tanh(T.dot(X, params[u]))     # use tanh function
#         X = h
#     pyx = T.dot(X, params[len(params) - 1])      # hidden -> output    
#     return pyx

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
                    factors = float(sequential_number[0])
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

def deep_neural_network():
    trX, trY = read_features()
    
    X = T.fmatrix()
    Y = T.fmatrix()    
    load_params = False
    hidden_layer = '6_layers/'       # = n_hidden layer below
    artic = 'artic/'
    measure = 'SQR/'
    id_file = 0
    weight_folder = '../weight_DNN/' + hidden_layer + measure + artic
    
    if not os.path.exists(weight_folder):
        os.makedirs(weight_folder)
        
    filename = weight_folder + 'Phonemic_DNN_SGD_id_' + str(id_file) + ".txt"
    
    if load_params:
        nloop,n_hidden_layer, n_input_f, n_hidden_f, n_output_f, params, bias = load_weight_info(filename)             
    else:
        print "load Initial"
        nloop = 0
        n_hidden_layer = 1
        n_input_f = 20
        n_hidden_f = 100
        n_output_f = 15
        params, bias = load_initial_info(n_hidden_layer, n_input_f, n_hidden_f, n_output_f)    
        
    trX = trX[:,1:n_input_f]
    trY = trY[:,1:n_output_f]
    #trX = trX[1:200,1:2]
    #trY = trY[1:200:,1:2]
    
    print trX.shape
    print trY.shape   
    print nloop,n_hidden_layer, n_input_f, n_hidden_f, n_output_f
    #print params
    print "_-----------"
    #print bias
    py_x = model(X, params, bias)
    
    y_x = py_x
    #cost = T.mean(T.nnet.categorical_crossentropy(py_x, Y))
    cost = T.mean(T.sqr(py_x - Y))
    
    updates = sgd(cost, params, bias)
#     for u in xrange(len(params)):
#         print params[u]
#         c = params[u].get_value()
#         print c.shape
#     for u in xrange(len(bias)):
#         print bias[u]
#         c = bias[u].get_value()
#         print c.shape
    #exit()
    train = theano.function(inputs=[X, Y], outputs=cost, updates=updates, allow_input_downcast=True)
    predict = theano.function(inputs=[X], outputs=y_x, allow_input_downcast=True)
    
    LOG_FILENAME = 'DNN.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
        
    for i in range(nloop, nloop + 10):
        print "i ", i
        #logging.debug('loop' + str(i))
        error_total = 0
        arr_X_Y = zip(range(0, len(trX), 128), range(128, len(trX), 128))
        #arr_X_Y = zip(range(0, len(trX), 1), range(1, len(trX), 1))
        
        for start, end in arr_X_Y:
            cost = train(trX[start:end], trY[start:end])
            error_total += cost
            #print cost
        print error_total
#         last_element = arr_X_Y[len(arr_X_Y)-1][0] 
#         if last_element < len(trX):
#             cost = train(trX[last_element: len(trX)], trY[last_element:len(trY)])    
#             error_total += cost
#         print error_total / len(trX)

        save_weight_info( filename, i, n_hidden_layer, n_input_f, n_hidden_f, n_output_f, params, error_total, bias)
        id_file = 1 - id_file
        filename = weight_folder + 'Phonemic_DNN_SGD_id_' + str(id_file) + ".txt"
        #exit()
    #plt.plot(trX,trY,'.')
    #plt.plot(trX,trX *  w.get_value() + b.get_value(), "red")
    exit()
    feature_out_dir = '/home/danglab/Phong/norm/output_norm/'
    test_dir = '/home/danglab/Phong/TestData/Features_Norm/minus/6dB/'
    dnn_predict_dir = '/home/danglab/DNN_Predict/DNN_Bias/'+ measure + artic + 'minus/6dB/'
    
    if not os.path.exists(dnn_predict_dir):
        os.makedirs(dnn_predict_dir)
        
    listtest = sorted(os.listdir(test_dir))
    cnt = 0
    for afile in listtest:
        #print afile                 #usctimit_ema_f1_001_005_100ms_noise_in.txt
        test_arr, factors = read_file_test(test_dir + afile, n_input_f, "factors")                                #read a missing_feature
        find_ = [m.start() for m in re.finditer('_', afile)]      
        file_mat = (afile.replace(afile[find_[4]:find_[6]],'')).replace('in.','out.')   #usctimit_ema_f1_001_005_out.txt
        #test_res_arr = read_file_test(feature_out_dir + file_mat, n_output_f)              #read an original output feature
        energy = test_arr[:,0]          #ko cho energy vao DNN
        test_arr = test_arr[:,1:n_input_f]
        print factors
        write_predict_2_file(dnn_predict_dir + afile.replace(afile[find_[5]:find_[6]],'').replace("_out",''), energy, predict(test_arr), factors)      # write result to file
             
def write_predict_2_file(filename, energy, res_arr, factors):
    files = open(filename, 'w')
    nframes = res_arr.shape[0]
    for i in xrange(nframes):
        files.write("%s "%(energy[i] * factors))        # restore energy
        for j in xrange(12):  #13
            files.write("%s " %(res_arr[i][j] * factors))
        files.write("\n")
    files.close()

deep_neural_network()