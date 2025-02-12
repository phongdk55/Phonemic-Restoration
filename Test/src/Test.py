import numpy as np
import theano
from theano import tensor as T
from numpy import dtype
import matplotlib.pyplot as plt
from theano.gof import cmodule

#http://deeplearning.net/software/theano/install_ubuntu.html#install-ubuntu
trX = np.linspace(-1,1,101)
trY = 2 * trX * np.random.rand(*trX.shape) * 0.33
#trY = trX * trX + np.random.rand(*trX.shape)

#print trX
X = T.scalar()
Y = T.scalar()

def model(X,w,b):
    return X * w + b

def floatX(X):
    return np.asarray(X, dtype=theano.config.floatX)

def init_weights(shape):
    return theano.shared(floatX(np.random.randn(*shape) * 0.01))

def quadratic_model(X,w, b):
    return X * X * w + b

def quadratic():
    trX = np.linspace(-1,1,101)
    trY = trX * trX + np.random.rand(*trX.shape)
    w = theano.shared(np.array(0.,dtype = theano.config.floatX))
    b = theano.shared(np.array(0.,dtype = theano.config.floatX))
    y = quadratic_model(X, w,b)
    
    cost = T.mean(T.sqr(y - Y))
    gradient = T.grad(cost= cost,wrt=[w,b])
    
    upates = [[w, w - gradient[0] * 0.01],[b,b - gradient[1]*0.01]]
    
    train = theano.function(inputs=[X,Y],outputs= cost, updates= upates, allow_input_downcast=True)
    
    for i in xrange(100):
        for x,y in zip(trX,trY):
            cs = train(x,y)
    print "cost ", cs

    print w.get_value(), b.get_value()
    
    plt.plot(trX,trY,'.')
    plt.plot(trX,trX * trX * w.get_value() + b.get_value(), "red") 
   
def linear():
    w = theano.shared(np.array(0.,dtype = theano.config.floatX))
    b = theano.shared(np.array(0.,dtype = theano.config.floatX))
    y = model(X, w,b)
    
    cost = T.mean(T.sqr(y - Y))
    gradient = T.grad(cost= cost,wrt=[w,b])
    
    upates = [[w, w - gradient[0] * 0.01],[b,b - gradient[1]*0.01]]
    
    train = theano.function(inputs=[X,Y],outputs= cost, updates= upates, allow_input_downcast=True)
    
    for i in xrange(100):
        for x,y in zip(trX,trY):
            cs = train(x,y)
    print "cost ", cs

    print w.get_value(), b.get_value()
    
    plt.plot(trX,trY,'.')
    plt.plot(trX,trX *  w.get_value() + b.get_value(), "red")
    #plt.show()    

def linear_2():
    w1 = theano.shared(np.array(0.,dtype = theano.config.floatX))
    y = X * w1
    
    cost = T.mean(T.sqr(y - Y))
    gradient = T.grad(cost= cost,wrt=w1)
    
    upates = [[w1, w1 - gradient * 0.01]]
    
    train = theano.function(inputs=[X,Y],outputs= cost, updates= upates, allow_input_downcast=True)
    
    for i in xrange(100):
        for x,y in zip(trX,trY):
            #print x,y
            cs = train(x,y)
       
    print "cost ", cs
    print w1.get_value()
    plt.plot(trX,trX *  w1.get_value(),'blue')
    
linear_2() 
plt.show() 
    

'''
a = T.scalar()
b = T.scalar()
y = a * b

multiply = theano.function(inputs=[a,b], outputs= y)

print multiply(3,2)
print multiply(4,5)
'''