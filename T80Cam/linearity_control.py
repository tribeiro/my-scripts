#!/usn/bin/env python

import sys,os
import numpy as np
import pylab as py
from scipy.interpolate import interp1d
from scipy.optimize import leastsq

def main(argv):
    _path = os.path.expanduser('~/Documents/linearity/model1_20160801')
    data_control = 'data_control.lis'
    data_lin = 'data_linearity.lis'

    data = np.loadtxt(os.path.join(_path,data_control),dtype='S',unpack=True)

    time = np.zeros(len(data[1]))
    for i in range(len(time)):
        hh,mm,ss = data[3][i].split(':')
        time[i] = float(hh)+float(mm)/60.+float(ss)/60./60.
        print hh,mm,ss,'=',time[i]
    reftime = time[0]
    time -= reftime

    ndata = np.zeros((len(data[0]),2,8))

    for i in range(len(data[0])):
        ndata[i] += np.load(data[0][i])

    ndata = ndata.T

    nfilter = 11
    niter = 3
    ff = []
    for i in range(2):
        h = []
        for j in range(8):
            data = ndata[j][i]# /ndata[0][0]
            # c0[i][j] = np.mean(data)
            # data/=np.mean(data[:nfilter])
            f = interp1d(time, data)
            print f
            dt = np.mean(time[1:]-time[:-1])
            xx= np.arange(time[0],time[-1],dt/10)
            # py.plot(time, data,'o')
            # py.plot(xx,f(xx),'r.')
            h.append(f)
            # break
        ff.append(h)
            # py.savefig(os.path.join(_path,
            #                         'array_%i_%i.png' % (i,j)))

            # if i == 1 and j in [3,4,5]:
    py.show()

    data = np.loadtxt(os.path.join(_path,data_lin),dtype='S',unpack=True)
    texp = np.array(data[1],dtype=float)
    ltime = np.zeros(len(data[1]))
    for i in range(len(ltime)):
        hh,mm,ss = data[3][i].split(':')
        ltime[i] = float(hh)+float(mm)/60.+float(ss)/60./60.

    ltime -= reftime # MUST BE time[0] and not ltime!!!!!

    ndata = np.zeros((len(data[0]),2,8))

    print ltime[0], f(ltime[0])
    for i in range(len(data[0])):
        ndata[i] += np.load(data[0][i])

    ndata = ndata.T

    coeffs = []

    for i in range(2):
        x_coeff = []
        for j in range(8):
            data = ndata[j][i]/ff[i][j](ltime)*np.mean(ff[i][j](ltime)) # /ndata[0][0]
            texp_unique = texp
            # py.plot(ltime,1./ff[i][j](ltime)*np.mean(ff[i][j](ltime)))
            # py.plot(data/ff[i][j](ltime)*np.mean(ff[i][j](ltime)))
            # py.show()
            # texp_unique = np.unique(texp)
            # data = np.zeros(len(texp_unique))
            # sigma = np.zeros(len(texp_unique))
            # for ii in range(len(texp_unique)):
            #     mm = texp == [texp_unique[ii]]
            #     data[ii] = np.mean(ndata[j][i][mm]*ff[i][j](ltime[mm])/np.mean(ff[i][j](ltime[mm])))
            #     sigma[ii] = np.std(ndata[j][i][mm])

            x = np.mean(ff[i][j](ltime))*texp_unique/10.
            # py.plot(x,data/x,'x')
            # py.show()
            # continue
            # p0 = data[0]
            # data /= p0
            # data -= 1.0
            # data *= 100.
            # print data
            mask = np.bitwise_and(data > 1e3, data < 62e3)
            print data
            texp_unique = data #np.mean(ff[i][j](ltime))*texp_unique/10.
            data = data/x

            c1 = np.polyfit(texp_unique[mask],data[mask],1)
            # if i == 1 and j in [2,3,4,5]:
            #     c2 = np.polyfit(texp_unique[mask],data[mask],17)
            # elif i == 0 and j in [2,3,7]:
            #     c2 = np.polyfit(texp_unique[mask],data[mask], 17)
            # else:
            c2 = np.polyfit(texp_unique[mask]/32767.,data[mask],17)
            # def fitfunc(p,x):
            #     return x*np.sum( np.array([p[i] * (x/32767.)**i for i in range(len(p))]) )
            #
            # errfunc = lambda p, x: fitfunc(p, x[0]) - x[1]
            # p0 = c2
            # p1, flag = leastsq(errfunc, p0, args=([texp_unique[mask],data[mask]],))

            x_coeff.append(c2)
            p1 = np.poly1d(c1)
            p2 = np.poly1d(c2)
            # p2 = interp1d(texp_unique[mask],data[mask],bounds_error=False, fill_value='extrapolate')
            py.subplot(111)
            # py.subplot(211)
            # py.subplot(2,8,1+j+8*i)
            # py.plot(data,'o')#,'bo')
            py.title('%i x %i' % (i,j))

            # py.plot(texp, data/p1(texp),'bo',mfc='w')#,'bo')
            maxpos = np.max(data[mask]-p1(texp_unique)[mask])
            maxneg = np.min(data[mask]-p1(texp_unique)[mask])

            print 'Non-linearity: %f ' % ( (maxpos-maxneg) / np.max(data[mask]) * 100,
                                                      )
            # py.plot(texp_unique, data/p1(texp_unique),'bo',mfc='w')#,'bo')
            # py.plot(texp_unique[mask], data[mask]/p1(texp_unique)[mask],'bo')#,'bo')

            # py.plot(texp[mask], data[mask],'bo')#,'bo')

            # py.subplot(212)
            py.subplot(211) # /ff[i][j](ltime)*np.mean(ff[i][j](ltime))
            py.plot(texp_unique, data,'bo',mfc='w')#,'bo')
            # py.plot(texp_unique, data/ff[i][j](ltime)*np.mean(ff[i][j](ltime)),'rx',mfc='w')#,'bo')
            py.plot(texp_unique[mask], data[mask],'bo')#,'bo')
            # # py.subplot(2,8,1+j+8*i)
            # # py.plot(data,'o')#,'bo')
            # py.title('%i x %i' % (i,j))
            xx = np.linspace(0.,70e3,200)
            # py.plot(data/ndata[0][0],'o')#,'bo')
            ylim = py.ylim()
            # print py.ylim()
            # py.plot([5e3,6e4],[0,0],'r:')
            # py.plot(xx,np.zeros_like(xx)+1,'r-')
            # py.plot(xx,p2(xx)/p1(xx),'g-')

            py.plot(xx,p1(xx),'r-')
            py.plot(xx,p2(xx/32767.),'g.')
            print p2(10e3/32767.), c2
            return
            # xx = np.linspace(np.min(texp)-1,np.max(texp)+1)
            py.ylim([0.9,1.1])

            py.subplot(212)
            # # py.plot(texp_unique, data-p2(texp_unique),'bo',mfc='w')#,'bo')
            py.plot(texp_unique[mask], data[mask]/p2(texp_unique/32767.)[mask],'bo')#,'bo')

            # py.plot(texp,ndata[j][i],'o')#,'bo')
            # xx = np.linspace(np.min(texp)-1,np.max(texp)+1)
            # py.plot(xx,p(xx),'r-')
            print os.path.join(_path,
                                    'array_%i_%i.png' % (i,j))
            # py.xlabel('Exposure time')
            # py.ylabel('Arr_%i_%i / Arr_0_0 [%%]' % (i, j))
            py.savefig(os.path.join(_path,
                                    'array_%i_%i.png' % (i,j)))

            # if i == 1 and j in [3,4,5]:
            # py.show()

            py.cla()
            # return
        coeffs.append(x_coeff)

    np.save('linearity_coeff.npy',
            np.array(coeffs))

    return 0

if __name__ == '__main__':
    main(sys.argv)