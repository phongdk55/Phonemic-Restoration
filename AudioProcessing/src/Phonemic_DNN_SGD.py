import theano
from theano import tensor as T
import numpy as np
from load_data_DNN_norm import read_features, read_file_test
import math
import os,re
import logging
from weight_matrix import save_weight_info, load_weight_info, load_initial_info

class Deep_Neural_Network():
    def __init__(self):
        self.space = False
        self.hidden_layer = '5_layers/'       # = n_hidden layer below
        self.artic = 'artic/noises/'             # type of testing audio - noise or space / type of whether using articulatory data or not
        
        self._training_DNN()
        self._testing_DNN()
        
    def _sgd(self,cost, params, lr=0.05):             # generalize to compute gradient descent
        grads = T.grad(cost=cost, wrt=params)   # on all model parameters
        updates = []
        for p, g in zip(params, grads):
            updates.append([p, p - g * lr])
        return updates

    def _model(self,X, params):         
        for u in xrange(len(params) - 1):
            h = T.tanh(T.dot(X, params[u]))     # use tanh function
            X = h
        pyx = T.dot(X, params[len(params) - 1])     # hidden -> output    
        return pyx

    def _training_DNN(self):
        trX, trY, self.missing_filename_list, self.test_number = read_features()        
        
        load_params = False
        
        id_file = 0
        weight_folder = '../weight_DNN/SQR/' + self.hidden_layer + self.artic + 'test_' + str(self.test_number) + '/'
        
        if not os.path.exists(weight_folder):
            os.makedirs(weight_folder)
            
        filename = weight_folder + 'Phonemic_DNN_SGD_id_' + str(id_file) + ".txt"
        
        if load_params:
            self.nloop,self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f, params = load_weight_info(filename)             
        else:
            self.nloop = 0
            self.n_hidden_layer = 5
            self.n_input_f = 109
            self.n_hidden_f = 512
            self.n_output_f = 37
            params = load_initial_info(self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f)    
            
        trX = trX[:,1:self.n_input_f]
        trY = trY[:,1:self.n_output_f]
        print trX.shape
        print trY.shape   
        print self.nloop, self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f
        
        X = T.fmatrix()
        Y = T.fmatrix()
        py_x = self._model(X, params)
        y_x = py_x
        #cost = T.mean(T.nnet.categorical_crossentropy(py_x, Y))
        cost = T.mean(T.sqr(py_x - Y))
        #params = [w_h, w_h1, w_h2, w_h3, w_o]
        updates = self._sgd(cost, params)
        train = theano.function(inputs=[X, Y], outputs=cost, updates=updates, allow_input_downcast=True)
        self.predict = theano.function(inputs=[X], outputs=y_x, allow_input_downcast=True)
        #LOG_FILENAME = 'DNN.log'
        #logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
              
        for i in range(self.nloop, self.nloop + 1000):
            print i
            #logging.debug('loop' + str(i))
            error_total = 0
            arr_X_Y = zip(range(0, len(trX), 128), range(128, len(trX), 128))
            for start, end in arr_X_Y:
                cost = train(trX[start:end], trY[start:end])
                error_total += cost
                #print cost
            last_element = arr_X_Y[len(arr_X_Y)-1][0] 
            if last_element < len(trX):
                cost = train(trX[last_element: len(trX)], trY[last_element:len(trY)])    
                error_total += cost
            print error_total / len(trX)
            save_weight_info( filename, i, self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f, params, error_total)
            id_file = 1 - id_file
            filename = weight_folder + 'Phonemic_DNN_SGD_id_' + str(id_file) + ".txt"
    
    def _testing_DNN(self):        
        if self.space:
            test_dir = '/home/danglab/Phong/TestData/Features_Norm_Space/'  
        else:
            test_dir = '/home/danglab/Phong/TestData/Features_Norm/'      
        
        for type_test in sorted(os.listdir(test_dir)):
            if not type_test.endswith('zip'):
                
                type_test_dir = test_dir + type_test + '/'
                print type_test_dir
                dnn_predict_dir = '/home/danglab/DNN_Predict/Features_Norm/' + self.hidden_layer +'SQR/' + self.artic + 'test_' + str(self.test_number) + '/' + type_test + '/'
        
                if not os.path.exists(dnn_predict_dir):
                    os.makedirs(dnn_predict_dir)
                print type_test
                duration = type_test.split('_')[1]     # 50ms, 100ms
                  
                #listtest = sorted(os.listdir(type_test_dir))
                #for afile in listtest:
                for prefix_file in self.missing_filename_list:
                    afile = prefix_file + '_' + duration + '_in.txt' 
                    test_arr, factors = read_file_test(type_test_dir + afile, self.n_input_f, "factors")                                #read a missing_feature
                    find_ = [m.start() for m in re.finditer('_', afile)]  
                    energy = test_arr[:,0]          #ko cho energy vao DNN
                    test_arr = test_arr[:,1:self.n_input_f]
                    #print factors
                    self._write_predict_2_file(dnn_predict_dir + afile.replace(afile[find_[4]:len(afile)-4],''), energy, self.predict(test_arr), factors)      # write result to file
             
    def _write_predict_2_file(self,filename, energy, res_arr, factors):
        files = open(filename, 'w')
        nframes = res_arr.shape[0]
        for i in xrange(nframes):
            files.write("%s "%(energy[i] * factors))        # restore energy
            for j in xrange(12):  #13
                files.write("%s " %(res_arr[i][j] * factors))
            files.write("\n")
        files.close()
        
Phonemic_DNN = Deep_Neural_Network()