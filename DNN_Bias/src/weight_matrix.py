import numpy as np
import theano

def save_weight_info(filename, nloop,n_hidden_layer, n_input_f, n_hidden_f, n_output_f, params, cost, bias):
    weight_file = open(filename,'w')
    weight_file.write("%s %s %s %s %s %s\n" %(nloop, n_hidden_layer,  n_input_f - 1, n_hidden_f, n_output_f - 1, cost))
    #print '*******************'
    print len(params)
    for w in params:
        a_matrix = w.get_value()
        print a_matrix.shape
        [m,n] = a_matrix.shape
        for i in xrange(m):
            for j in xrange(n):
                weight_file.write("%s " %(a_matrix[i,j]))
            weight_file.write("\n")
    print len(bias)
    for b in bias:
        b_vector = b.get_value()
        print b_vector.shape
        m = b_vector.shape[0]
        for i in xrange(m):
            #for j in xrange(n):
            weight_file.write("%s " %(b_vector[i]))
        weight_file.write("\n")
    weight_file.close()
    
def load_weight_info(filename):
    weight_file = open(filename,'r')
    cnt = 0
    for line in weight_file:
        #print line
        sequential_number = line.split()
        nloop = int(sequential_number[0])
        n_hidden_layer = int(sequential_number[1])
        n_input_f = int(sequential_number[2]) 
        n_hidden_f = int(sequential_number[3])
        n_output_f = int(sequential_number[4])
        break                                           # khi break thi dong 1 trong file da duoc doc, lan for sau thi doc tu dong thu 2
    weight_matrix = np.zeros((n_input_f + n_hidden_layer * n_hidden_f , max(n_input_f, n_hidden_f, n_output_f)))
    
    cnt = 0
    for line in weight_file:                #load all weight matrices into an array, after that devide it into smaller array
        #print line
        sequential_number = line.split()
        for u in xrange(len(sequential_number)):
            try:
                weight_matrix[cnt, u] = float(sequential_number[u])
            except:
                print ("Error when load_weight_info")
                exit()
        cnt+=1
        if cnt >= (n_input_f + n_hidden_layer * n_hidden_f):
            break  
        
    w_h = share_weights(weight_matrix[0:n_input_f, 0:n_hidden_f])      # input layer
    #print 0,n_input_f
    params = [w_h]
    
    for u in xrange(n_hidden_layer -1 ):
        w = share_weights(weight_matrix[n_input_f + u * n_hidden_f: n_input_f + (u+1) * n_hidden_f, 0: n_hidden_f])
        #print n_input_f + u * n_hidden_f, n_input_f + (u+1) * n_hidden_f
        params.append(w)
    w_o = share_weights(weight_matrix[n_input_f + (n_hidden_layer-1) * n_hidden_f: n_input_f + n_hidden_layer * n_hidden_f, 0: n_output_f ])
    #print n_input_f + (n_hidden_layer-1) * n_hidden_f, n_input_f + n_hidden_layer * n_hidden_f
    #print w_o[w_o.shape[0]-1]
    params.append(w_o)
    print "load weight --------------- ok"
    bias = []
    for line in weight_file:
        sequential_number = line.split()
        #b = np.zeros(n_hidden_f)
        b = []
        for u in xrange(len(sequential_number)):
            try:
                #b[u] = float(sequential_number[u])
                b.append(float(sequential_number[u]))
            except:
                print "Error when load bias from file "
                exit()
        
        bias.append(share_weights(b))
        
    return nloop,n_hidden_layer, n_input_f + 1, n_hidden_f, n_output_f + 1, params, bias

def load_initial_info(n_hidden_layer, n_input_f, n_hidden_f, n_output_f):
    w_h = share_weights(np.random.randn(*(n_input_f - 1, n_hidden_f)) * 0.01 )      # weight matrix input -> hidden layer - not use energy
    #b_h = share_weights(np.random.randn(*(1, n_hidden_f)) * 0.01 ) 
    
    b_h = share_weights(np.random.randn(*(n_hidden_f ,)) * 0.01 ) 
    params = [w_h]
    bias = [b_h]
    for u in xrange(n_hidden_layer -1 ):
        w = share_weights(np.random.randn(*(n_hidden_f, n_hidden_f)) * 0.01)        # weight matrix hidden layer -> hidden layer
        params.append(w)
        bias.append(b_h)            # append bias of hidden layer
        
    w_o = share_weights(np.random.randn(*(n_hidden_f, n_output_f - 1)) * 0.01)       # wieght matrix hidden layer -> hidden layer - not use energy
    params.append(w_o)
    
    b_o = share_weights(np.random.randn(*(n_output_f - 1,)) * 0.01)
    bias.append(b_o)
    #bias = 1
    return params, bias

def floatX(X):
    return np.asarray(X, dtype=theano.config.floatX)

def share_weights(arr):
    return theano.shared(floatX(arr))
'''
def read_file_test(filename, num_features):
    input_file = open(filename,'r')
    feature = np.zeros((num_features))
    arr = []
    for line in input_file:
        sequential_number = line.split(" ")
        #print sequential_number 
        feature = np.zeros((num_features))
        for i in xrange(num_features):
            try:
                feature[i] = (float(sequential_number[i]))
            except:
                continue
        arr.append(feature)
    return np.array(arr).astype(np.float32)
'''