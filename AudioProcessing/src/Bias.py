from theano import function, config, shared, sandbox, tensor, Out
import theano
import numpy
import time
from theano.sandbox.cuda.basic_ops import gpu_from_host
vlen = 10 * 30 * 768  # 10 x # cores x # threads per core
iters = 1000
#http://deeplearning.net/software/theano/tutorial/aliasing.html
rng = numpy.random.RandomState(22)

x = shared(numpy.asarray(rng.rand(vlen), theano.config.floatX))

f1 = function([], gpu_from_host(tensor.exp(x)))
f2 = function([],
              Out(gpu_from_host(tensor.exp(x)),
                  borrow=True))
t0 = time.time()
for i in xrange(iters):
    r = f1()
t1 = time.time()
no_borrow = t1 - t0
t0 = time.time()
for i in xrange(iters):
    r = f2()
t1 = time.time()
print 'Looping', iters, 'times took', no_borrow, 'seconds without borrow',
print 'and', t1 - t0, 'seconds with borrow.'
if numpy.any([isinstance(x.op, tensor.Elemwise) and
              ('Gpu' not in type(x.op).__name__)
              for x in f1.maker.fgraph.toposort()]):
    print 'Used the cpu'
else:
    print 'Used the gpu'