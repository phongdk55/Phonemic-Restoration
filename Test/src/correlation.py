import numpy as np

a = np.array([1,3,1,4,6,1])
b = np.array([1,3,-1,4,6,2])

r = np.corrcoef(a,b)[0,1]
# print r
# print  np.corrcoef(a,b + 5)[0,1]
# print  np.corrcoef(a,b - 5.5)[0,1]
# print  np.corrcoef(a,(b / 3.0 ) + 4)[0,1]
c = a[:3]
print c
print 13%9

