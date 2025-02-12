import theano
from theano import tensor as T
import numpy as np
from load_data import read_features, read_file_test
import math
import os,re
import logging
from weight_matrix import save_weight_info, load_weight_info, load_initial_info

class Deep_Neural_Network():
    def __init__(self):        
        self.hidden_layer = '5_layers/'       # = n_hidden layer below
        self.feature_dim_in = 145 
        self.feature_dim_out = 49
        #self.artic = 'artic/'             # type of testing audio - noise or space / type of whether using articulatory data or not
        self.test_number = 0
        self._load_parameters()
        self._training_DNN()
        #self._run_testing_DNN()
        
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
        load_params = False
        
        self.id_file = 0
        self.weight_folder = '../weight_no_mid_145/' + 'test_' + str(self.test_number) + '/'
        
        if not os.path.exists(self.weight_folder):
            os.makedirs(self.weight_folder)
            
        self.filename = self.weight_folder + 'id_' + str(self.id_file) + ".txt"
        
        if load_params:
            self.nloop,self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f, self.params, self.bias= load_weight_info(self.filename)             
        else:
            self.nloop = 0
            self.n_hidden_layer = 5
            self.n_input_f = 144 * 3 + 1 - 36       # bo 36 acoustic feature cua frame o giua de noi suy
            self.n_hidden_f = 1024
            self.n_output_f = 145 #49
            self.params, self.bias = load_initial_info(self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f)
    
    def _stack_segment(self, trX, trY):     # use 3 continuous segments to get result which is the middle segment
        [m,n] = trX.shape
        stack_X = np.zeros((m - 2 ,3*n - 36))
        #stack_Y = np.zeros((m - 2  ,trY.shape[1] ))        #49 features
        stack_Y = np.zeros((m-2,n))             #145 features
        for u in xrange(m-2):
            feature_mid = trX[u+1][36:n]        # ko dung du lieu acoustic cua frame giua
            stack_X[u] = np.concatenate((trX[u],feature_mid, trX[u+2]))
            #stack_Y[u] = trY[u+1]           # use 3 continuous segment to get result which is the middle segment
            stack_Y[u] = trX[u+1]           #145 feature lay tu X
        #stack_X[0] = np.concatenate((trX[0],trX[0],trX[1]))
        #stack_Y[0] = trY[0]
        #stack_X[m-1] = np.concatenate((trX[m-2],trX[m-1],trX[m-1]))
        #stack_Y[m-1] = trY[m-1]
        return stack_X, stack_Y
    def _stack_segment_test(self, trX):     # use 3 continuous segments to get result which is the middle segment
        [m,n] = trX.shape
        stack_X = np.zeros((m ,3*n - 36))
        for u in xrange(m-2):
            feature_mid = trX[u+1][36:n]        # ko dung du lieu acoustic cua frame giua
            stack_X[u+1] = np.concatenate((trX[u],feature_mid, trX[u+2]))
            
        stack_X[0] = np.concatenate((trX[0],trX[0][36:n],trX[1]))               #border processing
        stack_X[m-1] = np.concatenate((trX[m-2],trX[m-1][36:n],trX[m-1]))
        return stack_X
    
    def _training_DNN(self):   
        trX, trY, self.missing_filename_list,  = read_features(self.test_number, self.feature_dim_in, self.feature_dim_out) #self.n_output_f)     
        trX = trX[:,1:self.feature_dim_in]
        trY = trY[:,1:self.feature_dim_out]   #self.n_output_f]
        
        trX, trY = self._stack_segment(trX, trY)
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
        #test_dir = '/home/danglab/Phong/features/Space/'  
        #self._testing_noise_space(test_dir, 'space/')
        #test_dir = '/home/danglab/Phong/features/Noise/'
        #self._testing_noise_space(test_dir, 'noises/')
        #test_dir = '/home/danglab/Phong/features/origin/input/'
        #self._testing_original_file(test_dir, 'origin/')
        
        test_dir = '/home/danglab/Phong/features/Space/0_20ms_1_-6dB/'
        self._testing_space(test_dir, 'space/20ms/')
        #test_dir = '/home/danglab/Results/artic_inter/10ms/'
        #self._testing_aritc_interpolation(test_dir)
        
    def _testing_noise_space(self, test_dir, type_data):             
        for type_test in sorted(os.listdir(test_dir)):
            if (not type_test.endswith('zip')) and 'output' not in type_test:                
                type_test_dir = test_dir + type_test + '/'
                print type_test_dir
                dnn_predict_dir = '/home/danglab/Results/New_PR/' + type_data + 'SP_no_EMA/'+'test_' + str(self.test_number) + '/' + type_test + '/'
        
                if not os.path.exists(dnn_predict_dir):
                    os.makedirs(dnn_predict_dir)
                print type_test
                duration = type_test.split('_')[1]     # 50ms, 100ms
                  
                #listtest = sorted(os.listdir(type_test_dir))
                #for afile in listtest:
                for prefix_file in self.missing_filename_list:
                    afile = prefix_file + '_' + duration + '_in.txt' 
                    test_arr, factors = read_file_test(type_test_dir + afile, self.feature_dim_in, "factors")                                #read a missing_feature
                    find_ = [m.start() for m in re.finditer('_', afile)]  
                    energy = test_arr[:,0]          #ko cho energy vao DNN
                    test_arr = test_arr[:,1:self.feature_dim_in]
                    #test_arr[:,12:self.n_input_f] = 0           # remove articulatory data
                    #print factors
                    self._write_predict_2_file(dnn_predict_dir + afile.replace(afile[find_[4]:len(afile)-4],''), energy, self.predict(test_arr), factors)      # write result to file
    
    def _testing_space(self, test_dir, type_data):
        dnn_predict_dir = '/home/danglab/Results/New_PR/' + type_data + 'full_EMA/'+'test_' + str(self.test_number) + '/' 
        
        if not os.path.exists(dnn_predict_dir):
            os.makedirs(dnn_predict_dir)
          
        for afile in self.missing_filename_list:
            test_arr, factors = read_file_test(test_dir + afile + '_20ms_in.txt', self.feature_dim_in, "factors")                                #read a missing_feature
            #print factors
            energy = test_arr[:,0]          #ko cho energy vao DNN
            test_arr = test_arr[:,1:self.feature_dim_in]
            if "full_EMA" not in dnn_predict_dir:
                print "no_ema"
                test_arr[:,12:self.feature_dim_in] = 0  # remove articulatory data
            
            test_arr = self._stack_segment_test(test_arr)
            #position 0,2,4,6,... is missing audio, only test these parts
            test_missing_part = test_arr[0:test_arr.shape[0]:2]     # lay nhung frame bi mat du lieu
            no_missing_part = test_arr[1:test_arr.shape[0]:2]
            print test_missing_part.shape, no_missing_part.shape, test_arr.shape
            self._write_predict_missing(dnn_predict_dir + afile + '.txt', energy, self.predict(test_missing_part), no_missing_part, factors)      # write result to file
            
    def _write_predict_missing(self,filename, energy, miss, no_miss, factors):  
        #write the result of predict missing part to file(0,2,4,...) + write no-mising part (1,3,5..)
        files = open(filename, 'w')
        nframes= miss.shape[0] + no_miss.shape[0]
        pos =0
        for i in xrange(nframes):
            files.write("%s "%(energy[i]))        # restore energy
            if (i % 2 == 0):            # lay phan du , hai phan nay viet xen ke nhau
                res_arr = miss[pos]     # missing part
            else:
                res_arr = no_miss[pos]  # no-missing part
                pos += 1
                
            for j in xrange(12):  #MFCC
                files.write("%s " %(res_arr[j] * factors))
            for j in xrange(12,self.feature_dim_out-1):
                files.write("%s " %(res_arr[j]))
            files.write("\n")
        files.close()
        
    def _testing_original_file(self, test_dir, type_data):     
        dnn_predict_dir = '/home/danglab/Results/New_PR/' + type_data + 'full_EMA/'+'test_' + str(self.test_number) + '/' 
        
        if not os.path.exists(dnn_predict_dir):
            os.makedirs(dnn_predict_dir)
          
        for afile in self.missing_filename_list:
            test_arr, factors = read_file_test(test_dir + afile + '_in.txt', self.feature_dim_in, "factors")                                #read a missing_feature
            #print factors
            energy = test_arr[:,0]          #ko cho energy vao DNN
            test_arr = test_arr[:,1:self.feature_dim_in]
            if "full_EMA" not in dnn_predict_dir:
                print "no_ema"
                test_arr[:,12:self.feature_dim_in] = 0  # remove articulatory data
            
            test_arr  = self._stack_segment_test(test_arr)
            print test_arr.shape
            self._write_predict_2_file(dnn_predict_dir + afile + '.txt', energy, self.predict(test_arr), factors)      # write result to file
    
    def _testing_aritc_interpolation(self, test_dir):
        dnn_predict_dir = '/home/danglab/Results/New_PR/' + 'space/artic_inter/'+'test_' + str(self.test_number) + '/10ms/' 
        
        if not os.path.exists(dnn_predict_dir):
            os.makedirs(dnn_predict_dir)
          
        for afile in self.missing_filename_list:
            test_arr, factors = read_file_test(test_dir + afile + '_10ms_in.txt', self.feature_dim_in, "factors")                                #read a missing_feature
            #print factors
            energy = test_arr[:,0]          #ko cho energy vao DNN
            test_arr = test_arr[:,1:self.feature_dim_in]
            test_arr[:,12:self.feature_dim_in] = 0  # remove articulatory data
            self._write_predict_2_file(dnn_predict_dir + afile + '.txt', energy, self.predict(test_arr), factors)      # write result to file
    
    def _write_predict_2_file(self,filename, energy, res_arr, factors):
        files = open(filename, 'w')
        nframes= res_arr.shape[0]
        
        for i in xrange(nframes):
            files.write("%s "%(energy[i]))        # restore energy
            for j in xrange(12):  #MFCC
                files.write("%s " %(res_arr[i][j] * factors))
            for j in xrange(12,self.feature_dim_out-1):
                files.write("%s " %(res_arr[i][j]))
            files.write("\n")
        files.close()

Phonemic_DNN = Deep_Neural_Network()