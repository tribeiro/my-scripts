import os,sys
import numpy as np
import pylab as py

path = os.path.expanduser('~/Documents/jvar')

tmt01 = 'filtersObservations_5years.txt'

tmt_data = np.loadtxt(os.path.join(path,tmt01),unpack=True,usecols=(2,3,4,5)).reshape(-1,)
tmt_data.sort()
tmt_data = tmt_data[:-56]

nperiods = 500
Pgrid = np.logspace(0,np.log10(24.*7.),nperiods)/24. # hour in days

nsim = 10000
# ninside = np.zeros((nperiods,nsim),dtype=int)
bins=np.arange(0,15)-0.5

hist2d = np.zeros((nperiods,len(bins)-1))
nlost = np.zeros(nperiods)
nmax = np.zeros(nperiods)

progress = '|'
for i in range(nperiods):
    sys.stdout.write('\r[%03i]%s' % (i,progress))
    sys.stdout.flush()
    if i%(nperiods/10) == 0:
        progress+='-'
    P = Pgrid[i]
    ninside = np.zeros(nsim,dtype=int)
    for j in range(nsim):
        phase = tmt_data/P
        phase += np.random.random()
        phase -= np.floor(phase)

        # flux = np.zeros_like(phase)+1.
        mask = np.bitwise_or(phase<0.01,
                              phase>0.99)
        ninside[j] = np.sum(mask)
    hh,edges = np.histogram(ninside,bins=bins)
    hist2d[i]+=hh
    nlost[i] = np.sum(hh[:3])
    nmax[i] = np.argmax(hh)

print '| - [Done]'
# py.imshow(hist2d,interpolation='nearest',origin='lower',aspect='auto')

np.savetxt(os.path.join(path,'sol_'+tmt01),X=zip(Pgrid,nlost/nsim,nmax))


py.figure(1)

X,Y = np.meshgrid(np.array(bins,dtype=np.float),np.array(Pgrid,dtype=np.float))
# Z = np.vstack(newhist)
# print X.shape,newhist.shape

py.pcolor(X,Y,hist2d)

py.figure(2)

py.subplot(211)
py.plot(np.log10(Pgrid),nlost/nsim,ls='steps-mid')

py.subplot(212)
py.plot(np.log10(Pgrid),nmax,ls='steps-mid')

# py.hist2d(Pgrid,ninside,
#         bins=np.arange(0,np.max(ninside)+1)-0.5,
#         normed=True)

# print np.sum(mask)
# flux[mask] = 0.
# py.plot(phase,flux ,'o')
#
# py.show()
