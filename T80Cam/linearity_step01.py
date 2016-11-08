#!/usn/bin/env python

import sys,os
import numpy as np
import pylab as py
from scipy.interpolate import interp1d

def main(argv):
    _path = os.path.expanduser('~/Documents/linearity/mode1_20160816')
    data_control = 'data_control.lis'
    data_lin = 'data_linearity2.lis'
    # _path = os.path.expanduser('~/Documents/linearity/model1_20160801')
    # data_control = 'data_control.lis'
    # data_lin = 'data_linearity.lis'

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

    ff = []
    for i in range(2):
        h = []
        for j in range(8):
            data = ndata[j][i]
            f = interp1d(time, data)
            print f
            dt = np.mean(time[1:]-time[:-1])
            xx= np.arange(time[0],time[-1],dt/10)
            # py.subplot(211)
            py.plot(time, data,'o')
            py.plot(xx,f(xx),'r.')
            h.append(f)
            # break
            py.title('Control exposures')
            py.xlabel('time')
            py.ylabel('ADU/s')
            #py.show()
            py.savefig(os.path.join(_path,
                                    'linearity_control_%i_%i.png' % (i,j)))
            py.cla()
        ff.append(h)

    # py.show()

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

    dtype = []
    for i in range(2):
        for j in range(8):
            dtype.append(('counts_%i_%i' % (i,j),np.float))
            dtype.append(('gain_%i_%i'% (i,j),np.float))
            dtype.append(('mask_%i_%i'% (i,j),np.bool))
    rel_gain = np.zeros(len(ndata[0][0]),
                        dtype = dtype)
    for i in range(2):
        x_coeff = []
        for j in range(8):
            data = ndata[j][i]/ff[i][j](ltime)*np.mean(ff[i][j](ltime)) # /ndata[0][0]
            texp_unique = texp

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
            if i == 1 and j in [2,3,4,5]:
                c2 = np.polyfit(texp_unique[mask],data[mask],17)
            elif i == 0 and j in [2,3,7]:
                c2 = np.polyfit(texp_unique[mask],data[mask], 17)
            else:
                c2 = np.polyfit(texp_unique[mask],data[mask],17)

            x_coeff.append(c2)
            p1 = np.poly1d(c1)
            p2 = np.poly1d(c2)
            # p2 = interp1d(texp_unique[mask],data[mask],bounds_error=False, fill_value='extrapolate')
            py.subplot(111)

            py.title('%i x %i' % (i,j))

            # py.plot(texp, data/p1(texp),'bo',mfc='w')#,'bo')
            maxpos = np.max(data[mask]-p1(texp_unique)[mask])
            maxneg = np.min(data[mask]-p1(texp_unique)[mask])

            print 'Non-linearity: %f ' % ( (maxpos-maxneg) / np.max(data[mask]) * 100 )

            py.plot(texp_unique, data,'bo',mfc='w')#,'bo')
            py.plot(texp_unique[mask], data[mask],'bo')#,'bo')
            rel_gain['counts_%i_%i' % (i,j)] = data
            rel_gain['gain_%i_%i' % (i,j)] = texp_unique
            rel_gain['mask_%i_%i' % (i,j)] = mask
            print os.path.join(_path,
                                    'linearity_%i_%i.png' % (i,j))
            py.savefig(os.path.join(_path,
                                    'linearity_%i_%i.png' % (i,j)))


            py.cla()

    np.save('linearity_curve.npy',
            rel_gain)
    # np.save('linearity_coeff.npy',
    #         np.array(coeffs))

    return 0

if __name__ == '__main__':
    main(sys.argv)