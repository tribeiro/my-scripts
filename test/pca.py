
import os
import numpy as np
import scipy.optimize as optimization
import pylab as py
from sklearn.decomposition import PCA as sklearnPCA

isochrone = np.loadtxt(os.path.expanduser('~/Documents/T80S/isochrones.dat'),unpack=True)[8:8+12]

n = 3
sklearn_pca = sklearnPCA(n_components=n)

# ref_pca = sklearn_pca.fit_transform(isochrone).T
#
# isochrone = isochrone.T

# pc = np.zeros((n,len(isochrone)))
#
# print isochrone.shape
# print ref_pca.shape,pc.shape
#
#
# for i in range(len(isochrone)):
#     for nn in range(n):
#         pc[nn][i] = np.sum(ref_pca[nn]*isochrone[i])
#
# # for nn in range(n-1):
# #     py.plot(pc[nn][:16],pc[nn+1][:16],'o')
# #     py.plot(pc[nn][16:16*2],pc[nn+1][16:16*2],'o')
# #     py.plot(pc[nn][16*2:],pc[nn+1][16*2:],'o')
# #     py.show()
#
#
# zero_point = np.random.rand(12)
#
# new_isochrone = np.array(isochrone)
#
# for i in range(len(new_isochrone)):
#     new_isochrone[i] += zero_point

# new_isochrone = new_isochrone.T

# new_pca = sklearn_pca.fit_transform(new_isochrone).T
#
# new_isochrone = new_isochrone.T
#
# new_pc = np.zeros((n,len(new_isochrone)))

# for i in range(len(new_isochrone)):
#     for nn in range(n):
#         new_pc[nn][i] = np.sum(new_pca[nn]*new_isochrone[i])

# for nn in range(n-1):
#     py.plot(pc[nn][:16],pc[nn+1][:16],'bo')
#     py.plot(pc[nn][16:16*2],pc[nn+1][16:16*2],'ro')
#     py.plot(pc[nn][16*2:],pc[nn+1][16*2:],'go')
#
#     py.plot(new_pc[nn][:16],new_pc[nn+1][:16],'b+')
#     py.plot(new_pc[nn][16:16*2],new_pc[nn+1][16:16*2],'r+')
#     py.plot(new_pc[nn][16*2:],new_pc[nn+1][16*2:],'g+')
#
#     py.show()

def add_zero_point(params,xdata):
    xdataT = np.array(xdata.T,copy=True)
    # print xdataT.shape
    for i in range(len(xdataT)):
        xdataT[i] += params
    # xdataT = xdata.T
    return xdataT.T

def make_pca(params,xdata):
    xdataT = add_zero_point(params,xdata)
    new_pca = sklearn_pca.fit_transform(xdataT).T
    return new_pca

def auto_valores(pca,xdata):
    xdataT = xdata.T
    auto_val = np.zeros((n,len(xdataT)))

    for i in range(len(xdataT)):
        for nn in range(n):
            auto_val[nn][i] = np.sum(pca[nn]*xdataT[i])

    return auto_val

def func(params, xdata, ydata):
    new_pc = make_pca(params,xdata)[0]
    # ydata =
    # print ydata.shape, new_pc.shape
    # print ydata - new_pc
    return ydata - new_pc

# print pc.shape
# print func(zero_point,new_isochrone,pc[0]).shape


# sol,flag =  optimization.leastsq(func, x0, args=(new_isochrone, pc[0]))
# print zero_point
# print sol
# func(-zero_point,new_isochrone,pc[0])
zero_point = np.random.rand(12)+2
x0 = np.random.rand(12)

# print zero_point
new_isochrone = add_zero_point(zero_point,isochrone)

# # print pc[0] - zpts[0]
# print zero_point
# # print sol
pc1 = make_pca(np.zeros(12),isochrone)
pc2 = make_pca(np.zeros(12),new_isochrone)

sol,flag =  optimization.leastsq(func, -x0, args=(new_isochrone, pc1[0]))

pc30 = make_pca(x0,new_isochrone)
pc3s = make_pca(sol,new_isochrone)

print zero_point
print x0
print sol
zero_vec = sol+zero_point
print np.mean(zero_vec)
print zero_vec-np.mean(zero_vec)
print zero_vec-sol
#
# print pc[0] - zpts[0]
py.plot(pc1[0],pc1[1],'o')
py.plot(pc2[0],pc2[1],'+')
py.plot(pc3s[0],pc3s[1],'x')
py.plot(pc30[0],pc30[1],'^')
py.show()


