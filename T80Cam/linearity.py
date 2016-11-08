#!/usn/bin/env python

import sys,os
import numpy as np
import pylab as py

def main(argv):
    _path = os.path.expanduser('~/Documents/linearity/model1_20160801')
    # data_list = 'data_control.lis'
    data_list = 'data_linearity.lis'
    # _path = os.path.expanduser('~/Documents/linearity/mode5')

    data = np.loadtxt(os.path.join(_path,data_list),dtype='S',unpack=True)
    texp = np.array(data[1],dtype=float)

    ndata = np.zeros((len(data[0]),2,8))

    for i in range(len(data[0])):
        ndata[i] += np.load(data[0][i])

    ndata = ndata.T

    ref_data = ndata[0][0]

    for i in range(2):
        for j in range(8):
            # data = ndata[j][i]# /ndata[0][0]
            # texp_unique = np.unique(texp)
            # data = np.zeros(len(texp_unique))
            # sigma = np.zeros(len(texp_unique))
            # for ii in range(len(texp_unique)):
            #     mm = texp == [texp_unique[ii]]
            #     data[ii] = np.mean(ndata[j][i][mm])
            #     sigma[ii] = np.std(ndata[j][i][mm])

            # p0 = data[0]
            # data /= p0
            # data -= 1.0
            # data *= 100.
            # print data
            data = ndata[j][i]
            mask1 = np.bitwise_and(data > 5e3, data < 30e3)
            mask = np.bitwise_and(data > 1e3, data < 60e3)
            py.plot(ref_data[mask], data[mask]/ref_data[mask],'bo')#,'bo')

            c1 = np.polyfit(ref_data[mask1],data[mask1]/ref_data[mask1],1)
            c2 = np.polyfit(ref_data[mask],data[mask],3)
            # if i == 1 and j in [2,3,4,5]:
            #     c2 = np.polyfit(ref_data[mask],data[mask],11)
            # elif i == 0 and j in [2,3,7]:
            #     c2 = np.polyfit(ref_data[mask],data[mask], 7)
            # else:
            #     c2 = np.polyfit(ref_data[mask],data[mask],5)
            p1 = np.poly1d(c1)
            p2 = np.poly1d(c2)

            py.subplot(111)
            # py.subplot(211)
            # py.subplot(2,8,1+j+8*i)
            # py.plot(data,'o')#,'bo')
            py.title('%i x %i' % (i,j))

            # py.plot(texp, data/p1(texp),'bo',mfc='w')#,'bo')
            # maxpos = np.max(ref_data[mask]-p1(texp_unique)[mask])
            # maxneg = np.min(ref_data[mask]-p1(texp_unique)[mask])
            #
            #
            # print 'Non-linearity: %f' % ( (maxpos-maxneg) / np.max(data[mask]) * 100)
            py.plot(ref_data, p1(ref_data),'-')#,'bo')
            # py.plot(ref_data[mask], ndata[mask],'bo')#,'bo')
            # py.plot(texp_unique, data,'bo',mfc='w')#,'bo')
            # py.plot(texp_unique[mask], data[mask],'bo')#,'bo')

            # py.plot(texp[mask], data[mask],'bo')#,'bo')

            # py.subplot(212)
            # # py.subplot(211)
            # # py.subplot(2,8,1+j+8*i)
            # # py.plot(data,'o')#,'bo')
            # py.title('%i x %i' % (i,j))
            # xx = np.linspace(0.,70.,200)
            # py.plot(data/ndata[0][0],'o')#,'bo')
            # ylim = py.ylim()
            # print py.ylim()
            # py.plot([5e3,6e4],[0,0],'r:')
            # py.plot(xx,np.zeros_like(xx)+1,'r-')
            # py.plot(xx,p2(xx)/p1(xx),'g-')

            # py.plot(xx,p1(xx),'r-')
            # py.plot(xx,p2(xx),'g-')

            # xx = np.linspace(np.min(texp)-1,np.max(texp)+1)
            # py.ylim([0.99,1.01])

            # py.subplot(212)
            # py.plot(texp,ndata[j][i],'o')#,'bo')
            # xx = np.linspace(np.min(texp)-1,np.max(texp)+1)
            # py.plot(xx,p(xx),'r-')
            print os.path.join(_path,
                                    'array_%i_%i.png' % (i,j))
            py.xlabel('Exposur time')
            # py.ylabel('Arr_%i_%i / Arr_0_0 [%%]' % (i, j))
            py.savefig(os.path.join(_path,
                                    'array_%i_%i.png' % (i,j)))

            # if i == 1 and j in [3,4,5]:
            py.show()

            py.cla()
            # return

    return 0

if __name__ == '__main__':
    main(sys.argv)