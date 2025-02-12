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
#         for u in xrange(len(params) - 1):
#             h = T.tanh(T.dot(X, params[u]) + bias[u])    # use tanh function
#             X = h
#         pyx = T.dot(X, params[len(params) - 1]) + bias[len(params)-1]     # hidden -> output   
        pyx = X.copy()
        for u in xrange(len(params)):
            h = T.tanh(T.dot(pyx, params[u]) + bias[u])    # use tanh function
            pyx = h        
        return pyx           
   
    def _load_parameters(self):   
        load_params = True
        
        self.id_file = 0
        self.weight_folder = '../weight_new/' + 'test_' + str(self.test_number) + '/'
        
        if not os.path.exists(self.weight_folder):
            os.makedirs(self.weight_folder)
            
        self.filename = self.weight_folder + 'id_' + str(self.id_file) + ".txt"
        
        if load_params:
            self.nloop,self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f, self.params, self.bias= load_weight_info(self.filename)             
        else:
            self.nloop = 0
            self.n_hidden_layer = 5
            self.n_input_f = 144 * 5 + 1 - 36 * 3      # bo 36 acoustic feature cua frame o giua de noi suy
            self.n_hidden_f = 1024
            self.n_output_f = 48 * 3 + 1 #49
            self.params, self.bias = load_initial_info(self.n_hidden_layer, self.n_input_f, self.n_hidden_f, self.n_output_f)
    
    def _stack_segment(self, trX, trY):     # use 5 continuous segments to get results which are three middle segment
        [m,n] = trX.shape
        stack_X = np.zeros((m - 4 ,5*n - 36 * 3))
        #stack_Y = np.zeros((m - 2  ,trY.shape[1] ))        #49 features
        stack_Y = np.zeros((m-4,48 * 3))             #145 features
        for u in xrange(0, m-4):
            feature_u1 = trX[u+1][36:n].copy()        # ko dung du lieu acoustic cua frame giua
            feature_u2 = trX[u+2][36:n].copy()
            feature_u3 = trX[u+3][36:n].copy()
            
            stack_X[u] = np.concatenate((trX[u],feature_u1,feature_u2, feature_u3, trX[u+4]))
            #144 * 3
            #stack_Y[u] = np.concatenate((trX[u+1],trX[u+2], trX[u+3]))           #145 feature lay tu X
            #MFCC + pos 12 + 36 = 48
            stack_Y[u] = np.concatenate((trX[u+1][0:12],trX[u+1][36:72],trX[u+2][0:12],trX[u+2][36:72],trX[u+3][0:12],trX[u+3][36:72]))           
        return stack_X, stack_Y
    
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
        
        test_dir = '/home/danglab/Phong/features/origin/input/'
        self._testing_original_file(test_dir, 'origin/')
        test_dir = '/home/danglab/Phong/features/Space/0_20ms_1_-6dB/'
        self._testing_space(test_dir, 'space/20ms/')
        
        #test_dir = '/home/danglab/Results/artic_inter/20ms/'
        #self._testing_aritc_interpolation(test_dir)
        #test_dir = '/home/danglab/Results/space_inter/20ms/'
        #self._testing_aritc_interpolation(test_dir)
        
    def _testing_space(self, test_dir, type_data):
        dnn_predict_dir = '/home/danglab/Results/PR_ver2/' + type_data + 'no_EMA/'+'test_' + str(self.test_number) + '/' 
        
        if not os.path.exists(dnn_predict_dir):
            os.makedirs(dnn_predict_dir)
          
        for afile in self.missing_filename_list:
            test_arr, factors = read_file_test(test_dir + afile + '_20ms_in.txt', self.feature_dim_in, "factors")                                #read a missing_feature
            #print factors
            energy = test_arr[:,0]          #ko cho energy vao DNN
            test_arr = test_arr[:,1:self.feature_dim_in]
            self._write_predict_missing(dnn_predict_dir + afile + '.txt', energy, test_arr, factors)      # write result to file
            
    def _write_predict_missing(self,filename, energy, test_arr, factors):  
        #write the result of predict missing part to file(0,2,4,...) + write no-mising part (1,3,5..)
        files = open(filename, 'w')
        m,n = test_arr.shape
        
        u = 0
        while (u < m-4):
            #for u in xrange(2, m-4,4):        # 0,1 lien quan den phan bi mat o dau -> bo qua
            files.write("%s "%(energy[u]))        # restore energy
            for j in xrange(12):  #MFCC            
                files.write("%s " %(test_arr[u][j] * factors))
            for j in xrange(12,self.feature_dim_out-1):
                files.write("%s " %(test_arr[u][j]))
            files.write("\n")
            if (u % 4 == 2):
                feature_u1 = test_arr[u+1][36:n].copy()        # ko dung du lieu acoustic cua frame giua
                feature_u2 = test_arr[u+2][36:n].copy()
                feature_u3 = test_arr[u+3][36:n].copy()
                feature_u4 = test_arr[u+4].copy()        # 
                
                if "full_EMA" not in filename:
                    feature_u1[:] = 0      # remove articulatory of (2,3,4,5)
                    feature_u2[:] = 0
                    feature_u3[:] = 0
                    feature_u4[:][36:n] = 0               
                
                stack_X = np.zeros((1,612))         
                stack_X[0] = np.concatenate((test_arr[u],feature_u1,feature_u2, feature_u3, feature_u4))
                
                #print stack_X.shape
                res_arr =  self.predict(stack_X)    # missing part
                res_arr = res_arr.reshape((3, res_arr.shape[1]/3))      # tach lam 3 mang roi nhau
                
                for k in xrange(0,3):     # viet 4 freame lien tiep        3,4,5 tu (2,6)
                    files.write("%s "%(energy[u+k+1]))        # restore energy
                    for j in xrange(12):  #MFCC
                        files.write("%s " %(res_arr[k][j] * factors))
                    for j in xrange(12,self.feature_dim_out-1):
                        files.write("%s " %(res_arr[k][j]))
                    files.write("\n")    
                u += 4
            else:
                u += 1
        for i in xrange(u,m):
            files.write("%s "%(energy[i]))        # restore energy
            for j in xrange(12):  #MFCC            
                files.write("%s " %(test_arr[i][j] * factors))
            for j in xrange(12,self.feature_dim_out-1):
                files.write("%s " %(test_arr[i][j]))
            files.write("\n")
        files.close()
        
    def _testing_original_file(self, test_dir, type_data):     
        dnn_predict_dir = '/home/danglab/Results/PR_ver2/' + type_data + 'no_EMA/'+'test_' + str(self.test_number) + '/' 
        
        if not os.path.exists(dnn_predict_dir):
            os.makedirs(dnn_predict_dir)
          
        for afile in self.missing_filename_list:
            test_arr, factors = read_file_test(test_dir + afile + '_in.txt', self.feature_dim_in, "factors")                                #read a missing_feature
            #print factors
            energy = test_arr[:,0]          #ko cho energy vao DNN
            test_arr = test_arr[:,1:self.feature_dim_in]            
            self._write_predict_missing(dnn_predict_dir + afile + '.txt', energy, test_arr, factors)      # write result to file
    
    def _testing_aritc_interpolation(self, test_dir):
        dnn_predict_dir = '/home/danglab/Results/PR_ver2/' + 'space/space_inter/'+'test_' + str(self.test_number) + '/20ms/' 
        
        if not os.path.exists(dnn_predict_dir):
            os.makedirs(dnn_predict_dir)
          
        for afile in self.missing_filename_list:
            test_arr, factors = read_file_test(test_dir + afile + '.txt', self.feature_dim_in, "factors")                                #read a missing_feature
            #print factors
            energy = test_arr[:,0]          #ko cho energy vao DNN
            test_arr = test_arr[:,1:self.feature_dim_in]
            #test_arr[:,12:self.feature_dim_in] = 0  # remove articulatory data
            #self._write_predict_2_file(dnn_predict_dir + afile + '.txt', energy, self.predict(test_arr), factors)      # write result to file
            self._write_predict_missing(dnn_predict_dir + afile + '.txt', energy, test_arr, factors)      # write result to file

Phonemic_DNN = Deep_Neural_Network()