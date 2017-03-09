
import os
import numpy as np
import scipy.optimize as optimization
import pylab as py
from sklearn.decomposition import PCA as sklearnPCA

isochrone = np.loadtxt(os.path.expanduser('~/Documents/T80S/isochrones.dat'),unpack=True)[8:8+12]
mass = np.loadtxt(os.path.expanduser('~/Documents/T80S/isochrones.dat'),unpack=True)[2]

n = 3
sklearn_pca = sklearnPCA(n_components=n)

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
    # xdataT = xdataT.T
    # new_pc = np.zeros((n,len(xdataT)))
    #
    # for i in range(len(xdataT)):
    #     for nn in range(n):
    #         new_pc[nn][i] = np.sum(new_pca[nn]*xdataT[i])
    #
    # return new_pc

def func(params, xdata, ydata):
    new_pc = make_pca(params,xdata)[0]
    # ydata =
    # print ydata.shape, new_pc.shape
    # print ydata - new_pc
    return ydata - new_pc

sigma = np.random.normal(scale=0.25,size=isochrone.shape)
print np.mean(sigma),np.std(sigma)
isochrone_MC = np.array(isochrone+sigma,copy=True)
NSIM = 3
print isochrone_MC.shape
isochrone = isochrone.T

for sim in range(NSIM):
    # sigma = np.random.normal(scale=0.1,size=isochrone.shape)
    # isochrone_MC = np.append(isochrone_MC,isochrone+sigma,axis=1)
    iso = []

    nstars = np.random.randint(3,30,isochrone.shape[0])
    for i in range(isochrone.shape[0]):
        nstars = np.random.randint(np.ceil(np.exp(- ( (mass[i]-1.)/0.8)**2.)*3.0),
                                   np.ceil(np.exp(- ( (mass[i]-1.)/0.8)**2.)*30.0),
                                   isochrone.shape[0])[0]
        for j in range(nstars):
            sigma = np.random.normal(scale=0.01,size=isochrone.shape[1])*isochrone[i]
            # print isochrone[i]+sigma
            iso.append(isochrone[i]+sigma)
            # iso = np.append(iso,
            #                 isochrone[i]+sigma,
            #                 axis=1)

    iso = np.array(iso).T
    # print iso.shape
    isochrone_MC = np.append(isochrone_MC,np.array(iso),axis=1)
        # print sim,np.random.randint(3,30,1)


zero_point_offset = np.random.rand(12)
x0 = np.random.rand(12)

# print zero_point
new_isochrone_MC = add_zero_point(zero_point_offset,isochrone_MC)

# isochrone_MC = isochrone_MC.T
isochrone = isochrone.T
pca1 = make_pca(np.zeros(12),isochrone)
print pca1.shape

sol,flag =  optimization.leastsq(func, -x0, args=(new_isochrone_MC, pca1[0]))
print zero_point_offset
print x0
print sol
zero_vec = sol+zero_point_offset
print np.mean(zero_vec)
print np.mean(zero_vec)-zero_vec
print zero_vec-sol

# pca2 = make_pca(np.zeros(12),isochrone_MC)
pca2 = make_pca(sol,new_isochrone_MC)

# py.hist2d(pca2[0]/np.sqrt(isochrone_MC.shape[1]),pca2[1]/np.sqrt(isochrone_MC.shape[1]),bins=100)
#
# print isochrone.shape
#
py.plot(pca2[0]/np.sqrt(isochrone_MC.shape[1]),pca2[1]/np.sqrt(isochrone_MC.shape[1]),'o')
py.plot(pca1[0]/np.sqrt(isochrone.shape[1]),pca1[1]/np.sqrt(isochrone.shape[1]),'r-')
py.show()