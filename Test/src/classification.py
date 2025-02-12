import theano
from theano import tensor as T
import numpy as np
from numpy import dtype
import matplotlib.pyplot as plt
from theano.gof import cmodule

#http://deeplearning.net/software/theano/install_ubuntu.html#install-ubuntu
trX = np.linspace(-1,1,101)
#trY = 2 * trX * np.random.rand(*trX.shape) * 0.33
trY = trX * trX + np.random.rand(*trX.shape)

#print trX
X = T.scalar()
Y = T.scalar()

def floatX(X):
    return np.asarray(X, dtype=theano.config.floatX)

def init_weights(shape):
    return theano.shared(floatX(np.random.randn(*shape) * 0.01))

def model(X, w):
    return T.nnet.softmax(T.dot(X, w))

def classify():
    trX = [(-1,1),(-1,0),(0,1),(0,0),(1,0)]
    trY = [(0,1),(1,0),(1,0),(0,1),(0,1)]

    teX = [(-1,2),(-0.5,0.5),(0,-1)]
    teY = [(1,0),(1,0),(0,1)]
    X = T.fmatrix()
    Y = T.fmatrix()
    
    w = init_weights((2, 2))
    
    py_x = model(X, w)
    y_pred = T.argmax(py_x, axis=1)
    
    cost = T.mean(T.nnet.categorical_crossentropy(py_x, Y))
    gradient = T.grad(cost=cost, wrt=w)
    update = [[w, w - gradient * 0.05]]
    
    train = theano.function(inputs=[X, Y], outputs=cost, updates=update, allow_input_downcast=True)
    predict = theano.function(inputs=[X], outputs=y_pred, allow_input_downcast=True)
    
    for i in range(20):
        for start, end in zip(range(0, len(trX), 2), range(2, len(trX), 2)):
            cost = train(trX[start:end], trY[start:end])
        print i, np.mean(np.argmax(teY, axis=1) == predict(teX))
    print "w ", w.get_value()
    #plt.plot(trX,trY,'.')
    #plt.plot(trX,trX * trX * w.get_value() + b.get_value(), "red") 

classify()
#plt.show() 