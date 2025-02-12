'''
import theano
from theano import tensor as T
import numpy as np
from numpy import dtype
import matplotlib.pyplot as plt
from theano.gof import cmodule

#http://deeplearning.net/software/theano/install_ubuntu.html#install-ubuntu
trX = np.linspace(-1,1,101)
trY = 2 * trX * np.random.rand(*trX.shape) * 0.33


#print trX
X = T.scalar()
Y = T.scalar()

def model(X,w,b):
    return X * w + b

w = theano.shared(np.array(0.,dtype = theano.config.floatX))
b = theano.shared(np.array(0.,dtype = theano.config.floatX))

print w.get_value()

y = model(X, w,b)

cost = T.mean(T.sqr(y - Y))
gradient = T.grad(cost= cost,wrt=w)

upates = [[w, w - gradient * 0.01],[b,b - gradient*0.01]]

train = theano.function(inputs=[X,Y],outputs= cost, updates= upates, allow_input_downcast=True)

for i in xrange(100):
    for x,y in zip(trX,trY):
        train(x,y)

print w.get_value(), b.get_value()

plt.plot(trX,trY,'.')
plt.plot(trX,trX *  w.get_value())
plt.show()    
'''
import numpy as np
a = np.array([1,2,3,20,5])
print a
b = np.array([3,2,1,4,6])

c = zip(range(0,11,3),range(0,11,3))
print len(c)
print c