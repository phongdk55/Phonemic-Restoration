import theano
from theano import tensor as T
import numpy as np
from load_data_DNN_norm import load_data, read_features
import math
import os,re
import logging

def floatX(X):
    return np.asarray(X, dtype=theano.config.floatX)

def init_weights(shape):
    return theano.shared(floatX(np.random.randn(*shape) * 0.01))

def sgd(cost, params, lr=0.05):             # generalize to compute gradient descent
    grads = T.grad(cost=cost, wrt=params)   # on all model parameters
    updates = []
    for p, g in zip(params, grads):
        updates.append([p, p - g * lr])
    return updates
'''
def model(X, w_h, w_o):         # 2 layers of computation 
    h = T.nnet.sigmoid(T.dot(X, w_h))       # input -> hidden(signmoid)
    #pyx = T.nnet.softmax(T.dot(h, w_o))     # hidden -> output(softmax)
    pyx = T.nnet.sigmoid(T.dot(h, w_o))     # hidden -> output(softmax)
    return pyx
'''
def model(X, w_h, w_h1, w_h2, w_h3, w_o):         # 2 layers of computation 
    
    #h = T.nnet.sigmoid(T.dot(X, w_h))       # input -> hidden(signmoid)
    #h1 = T.nnet.sigmoid(T.dot(h, w_h1))       # hidden -> hidden(signmoid)
    #h2 = T.nnet.sigmoid(T.dot(h1, w_h2))       # hidden -> hidden(signmoid)
    #pyx = T.nnet.softmax(T.dot(h, w_o))     # hidden -> output(softmax)
    #pyx = T.nnet.sigmoid(T.dot(h2, w_o))     # hidden -> output(softmax)
    
    h = T.tanh(T.dot(X, w_h))       # input -> hidden(tanh)
    h1 = T.tanh(T.dot(h, w_h1))       # hidden -> hidden(tanh)
    h2 = T.tanh(T.dot(h1, w_h2))       # hidden -> hidden(tanh)
    h3 = T.tanh(T.dot(h2, w_h3))
    #pyx = T.nnet.softmax(T.dot(h, w_o))     # hidden -> output(softmax)
    #pyx = T.tanh(T.dot(h2, w_o))     # hidden -> output(softmax)
    pyx = T.dot(h3, w_o)     # hidden -> output
    return pyx

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
    trX = trX[:,1:109]
    trY = trY[:,1:37]
    print trX.shape
    print trY.shape
    X = T.fmatrix()
    Y = T.fmatrix()    
    
    n_input_f = 109
    nNeural = 512
    n_output_f = 37
    
    w_h = init_weights((n_input_f - 1, nNeural))        # ko dung energy
    w_h1 = init_weights((nNeural, nNeural))
    w_h2 = init_weights((nNeural, nNeural))
    w_h3 = init_weights((nNeural, nNeural))
    w_o = init_weights((nNeural, n_output_f - 1))       # ko dung energy
    
    py_x = model(X, w_h, w_h1,w_h2, w_h3, w_o)
    y_x = py_x
    
    #cost = T.mean(T.nnet.categorical_crossentropy(py_x, Y))
    cost = T.mean(T.sqr(py_x - Y))
    params = [w_h, w_h1, w_h2, w_h3, w_o]
    updates = sgd(cost, params)
    train = theano.function(inputs=[X, Y], outputs=cost, updates=updates, allow_input_downcast=True)
    predict = theano.function(inputs=[X], outputs=y_x, allow_input_downcast=True)
    
    LOG_FILENAME = 'DNN.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    
    for i in range(1000):
        print i
        #logging.debug('loop' + str(i))
        for start, end in zip(range(0, len(trX), 128), range(128, len(trX), 128)):
            cost = train(trX[start:end], trY[start:end])      
    
    feature_out_dir = '/home/danglab/Phong/norm/output_norm/'
    test_dir = '/home/danglab/Phong/TestData/Features_Norm/minus/3dB/'
    dnn_predict_dir = '/home/danglab/DNN_Predict/norm/noenergy/minus/3dB/'
    
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
        write_predict_2_file(dnn_predict_dir + file_mat.replace("_out",''), energy, predict(test_arr), factors)      # write result to file
             
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