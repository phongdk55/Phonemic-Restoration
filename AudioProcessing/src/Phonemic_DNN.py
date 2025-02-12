import theano
from theano import tensor as T
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams
import numpy as np
from load_data_DNN import load_data
#http://unix.stackexchange.com/questions/52703/using-atlas-from-scipy

#srng = RandomStreams()

def floatX(X):
    return np.asarray(X, dtype=theano.config.floatX)

def init_weights(shape):
    return theano.shared(floatX(np.random.randn(*shape) * 0.01))

def rectify(X):                     #rectifier
    return T.maximum(X, 0.)

def softmax(X):                     # numerically stable softmax
    e_x = T.exp(X - X.max(axis=1).dimshuffle(0, 'x'))
    return e_x / e_x.sum(axis=1).dimshuffle(0, 'x')

def RMSprop(cost, params, lr=0.001, rho=0.9, epsilon=1e-6):
    grads = T.grad(cost=cost, wrt=params)
    updates = []
    for p, g in zip(params, grads):
        # a running average of the magnitude of the gradient
        acc = theano.shared(p.get_value() * 0.)     
        acc_new = rho * acc + (1 - rho) * g ** 2
        
        #scale the gradient based on runing average
        gradient_scaling = T.sqrt(acc_new + epsilon)
        g = g / gradient_scaling
        updates.append((acc, acc_new))
        updates.append((p, p - lr * g))
    return updates

def dropout(X, p=0.):       # randomly drop values and scale rest
    if p > 0:
        retain_prob = 1 - p
        X *= srng.binomial(X.shape, p=retain_prob, dtype=theano.config.floatX)
        X /= retain_prob
    return X

def model(X, w_h, w_h2, w_o, p_drop_input, p_drop_hidden):
    X = dropout(X, p_drop_input)        # noise inject into model rectifiers now used 2 hidden layers
    h = rectify(T.dot(X, w_h))          

    h = dropout(h, p_drop_hidden)
    h2 = rectify(T.dot(h, w_h2))

    h2 = dropout(h2, p_drop_hidden)
    #py_x = softmax(T.dot(h2, w_o))
    py_x = T.nnet.sigmoid(T.dot(h2, w_o))
    
    return h, h2, py_x

#trX, teX, trY, teY = mnist(onehot=True)
trX, trY, factor_data = load_data()

X = T.fmatrix()
Y = T.fmatrix()

w_h = init_weights((108, 625)) #init_weights((784, 625))
w_h2 = init_weights((625, 625))
w_o = init_weights((625, 36))

noise_h, noise_h2, noise_py_x = model(X, w_h, w_h2, w_o, 0.2, 0.5)
h, h2, py_x = model(X, w_h, w_h2, w_o, 0., 0.)
#y_x = T.argmax(py_x, axis=1)
y_x = py_x

cost = T.mean(T.nnet.categorical_crossentropy(noise_py_x, Y))
params = [w_h, w_h2, w_o]
updates = RMSprop(cost, params, lr=0.001)

train = theano.function(inputs=[X, Y], outputs=cost, updates=updates, allow_input_downcast=True)
predict = theano.function(inputs=[X], outputs=y_x, allow_input_downcast=True)

for i in range(200):
    print i
    for start, end in zip(range(0, len(trX), 128), range(128, len(trX), 128)):
        cost = train(trX[start:end], trY[start:end])
    if i == 199:
        print trY[0][0:12]
        print predict(trX)[0][0:12]
    print np.mean(np.square(trY[:][0:12] - predict(trX)[0:12]))

