import theano
from theano import tensor as T
import numpy as np
from load_data_DNN import read_features, read_file_test
import math
import os,re
import logging
from weight_matrix import save_weight_info, load_weight_info, load_initial_info

class Deep_Neural_Network():
    def __init__(self):        
        self.hidden_layer = '5_layers/'       # = n_hidden layer below
        #self.artic = 'artic/'             # type of testing audio - noise or space / type of whether using articulatory data or not
        self.test_number = 0
        self._load_parameters()
        self._training_DNN()
        self._run_testing_DNN()
        
    def _sgd(self,cost, params, bias, lr=0.05):             # generalize to compute gradient descent
        updates = []
        
        grads = T.grad(cost=cost, wrt=params)   # on all model parameters
        for p, g in zip(params, grads):
            updates.append([p, p - g * lr])
         
        grads = T.grad(cost=cost,wrt=bias)
        for p, g in zip(bias, grads):
            updates.append([p, p - g * lr])
        
        return updates
    
    def _model(self,X, params, bias):            # bias kich thuoc 1 * m, chi chay duoc voi tung frame, ko chay duoc vs nhieu frame 1 luc
        for u in xrange(len(params) - 1):
            h = T.tanh(T.dot(X, params[u]) + bias[u])    # use tanh function
            X = h
        pyx = T.dot(X, params[len(params) - 1]) + bias[len(params)-1]     # hidden -> output   
        
        return pyx           
   
    def _load_parameters(self):   
        load_params = True
        
        self.id_file = 0
        self.weight_folder = '../weight/' + 'test_' + str(self.test_number) + '/'
        
        if not os.path.exists(self.weight_folder):
            os.makedirs(self.weight_folder)
            
        self.filename = self.weight_folder + 'id_' + str(self.id_file) + ".txt"
        
        if load_params:
            self.nloop,self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f, self.params, self.bias= load_weight_info(self.filename)             
        else:
            self.nloop = 0
            self.n_hidden_layer = 5
            self.n_input_f = 145
            self.n_hidden_f = 1024
            self.n_output_f = 49
            self.params, self.bias = load_initial_info(self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f)
        
    def _training_DNN(self):   
        trX, trY, self.missing_filename_list,  = read_features(self.test_number, self.n_input_f, self.n_output_f)     
        trX = trX[:,1:self.n_input_f]
        trY = trY[:,1:self.n_output_f]
        print trX.shape
        print trY.shape   
        print self.nloop, self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f
        
        X = T.fmatrix()
        Y = T.fmatrix()
        py_x = self._model(X, self.params, self.bias)
        y_x = py_x
        cost = T.mean(T.sqr(py_x - Y))
        updates = self._sgd(cost, self.params, self.bias)
        train = theano.function(inputs=[X, Y], outputs=cost, updates=updates, allow_input_downcast=True)
        self.predict = theano.function(inputs=[X], outputs=y_x, allow_input_downcast=True)
              
        for i in range(self.nloop, self.nloop + 0 ):
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
            save_weight_info( self.filename, i, self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f, self.params, error_total, self.bias)
            self.id_file = 1 - self.id_file
            self.filename = self.weight_folder + 'id_' + str(self.id_file) + ".txt"            
            
    def _run_testing_DNN(self):
        test_dir = '/home/danglab/Phong/features/Space/'  
        self._testing_noise_space(test_dir, 'space/')
        #test_dir = '/home/danglab/Phong/features/Noise/'
        #self._testing_noise_space(test_dir, 'noises/')
        #test_dir = '/home/danglab/Phong/features/origin/input/'
        #self._testing_original_file(test_dir, 'origin/')
        
        #test_dir = '/home/danglab/Results/artic_inter/10ms/'
        #self._testing_aritc_interpolation(test_dir)
        
    def _testing_noise_space(self, test_dir, type_data):             
        for type_test in sorted(os.listdir(test_dir)):
            if (not type_test.endswith('zip')) and 'output' not in type_test:                
                type_test_dir = test_dir + type_test + '/'
                print type_test_dir
                dnn_predict_dir = '/home/danglab/Results/PhonemicRestoration/' + self.hidden_layer + type_data + 'SP_full_EMA/'+'test_' + str(self.test_number) + '/' + type_test + '/'
        
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
                    #test_arr[:,12:self.n_input_f] = 0           # remove articulatory data
                    #print factors
                    self._write_predict_2_file(dnn_predict_dir + afile.replace(afile[find_[4]:len(afile)-4],''), energy, self.predict(test_arr), factors)      # write result to file
    
    def _testing_original_file(self, test_dir, type_data):     
        dnn_predict_dir = '/home/danglab/Results/PhonemicRestoration/' + self.hidden_layer + type_data + 'no_EMA/'+'test_' + str(self.test_number) + '/' 
        
        if not os.path.exists(dnn_predict_dir):
            os.makedirs(dnn_predict_dir)
          
        for afile in self.missing_filename_list:
            test_arr, factors = read_file_test(test_dir + afile + '_in.txt', self.n_input_f, "factors")                                #read a missing_feature
            #print factors
            energy = test_arr[:,0]          #ko cho energy vao DNN
            test_arr = test_arr[:,1:self.n_input_f]
            test_arr[:,12:self.n_input_f] = 0  # remove articulatory data
            self._write_predict_2_file(dnn_predict_dir + afile + '.txt', energy, self.predict(test_arr), factors)      # write result to file
    
    def _testing_aritc_interpolation(self, test_dir):
        dnn_predict_dir = '/home/danglab/Results/PhonemicRestoration/' + self.hidden_layer + 'space/artic_inter/'+'test_' + str(self.test_number) + '/10ms/' 
        
        if not os.path.exists(dnn_predict_dir):
            os.makedirs(dnn_predict_dir)
          
        for afile in self.missing_filename_list:
            test_arr, factors = read_file_test(test_dir + afile + '_10ms_in.txt', self.n_input_f, "factors")                                #read a missing_feature
            #print factors
            energy = test_arr[:,0]          #ko cho energy vao DNN
            test_arr = test_arr[:,1:self.n_input_f]
            #test_arr[:,12:self.n_input_f] = 0  # remove articulatory data
            self._write_predict_2_file(dnn_predict_dir + afile + '.txt', energy, self.predict(test_arr), factors)      # write result to file
    
    def _write_predict_2_file(self,filename, energy, res_arr, factors):
        files = open(filename, 'w')
        (nframes, nfeatures )= res_arr.shape
        
        for i in xrange(nframes):
            files.write("%s "%(energy[i]))        # restore energy
            for j in xrange(12):  #MFCC
                files.write("%s " %(res_arr[i][j] * factors))
            for j in xrange(12,nfeatures):
                files.write("%s " %(res_arr[i][j]))
            files.write("\n")
        files.close()

Phonemic_DNN = Deep_Neural_Network()