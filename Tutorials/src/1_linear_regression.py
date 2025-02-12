import theano
from theano import tensor as T
import numpy as np

trX = np.linspace(-1, 1, 101)
trY = 2 * trX + np.random.randn(*trX.shape) * 0.33      # training data generation

X = T.scalar()              #symbolic variable initialization
Y = T.scalar()

def model(X, w):        #our model
    return X * w

w = theano.shared(np.asarray(0., dtype=theano.config.floatX))       #model parameter initialization
y = model(X, w)

cost = T.mean(T.sqr(y - Y))             #metric to be optimized by model
gradient = T.grad(cost=cost, wrt=w)     # learning signal for parameters
updates = [[w, w - gradient * 0.01]]    # how to change parameter based on learning signal

#compiling to a python function
train = theano.function(inputs=[X, Y], outputs=cost, updates=updates, allow_input_downcast=True)

for i in range(100):        # iterate through data 100 times and train model on each example of input, output pairs
    for x, y in zip(trX, trY):
        train(x, y)
        
print w.get_value() #something around 2

