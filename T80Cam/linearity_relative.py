import sys,os
import numpy as np
from matplotlib import pyplot as py
import yaml

def main(argv):
    _path = os.path.expanduser('~/Documents/linearity')
    filelist_name = 'filelist_mode1_20160801.lis'
    file_list_names_control = 'mode1/20160801/control.lis'
    file_list_names_lintest = 'mode1/20160801/linearity.lis'

    filelist = np.loadtxt(os.path.join(_path,filelist_name),dtype='S')
    filelist_control = np.loadtxt(os.path.join(_path,file_list_names_control),dtype='S',unpack=True)
    filelist_lintest = np.loadtxt(os.path.join(_path,file_list_names_lintest),dtype='S',unpack=True)

    with open(os.path.join(os.path.dirname(__file__),'linfit.yaml'),'r') as fp:
        config = yaml.load(fp)

    data = np.zeros((len(filelist_control[0]),2,8))

    for i in range(len(filelist_control[0])):
        data[i] += np.load(os.path.join(_path,filelist_control[0][i]))['global_median']
    data = data.T

    narr = 0
    lincorr = np.zeros((2,8),dtype=[('type', np.int),
                                    ('c1_1',np.float),
                                    ('c1_2',np.float),
                                    ('c1_3',np.float),
                                    ('break',np.float),
                                    ('step',np.float),
                                    ('c2_1',np.float),
                                    ('c2_2',np.float),
                                    ('c2_3',np.float),
                                    ('c2_4',np.float),
                                    ('c2_5',np.float),])
    for column in range(2):
        for line in range(8):

            # line,column = 4,1
            norm = np.mean(data[0][0]/data[line][column])

            ldata = np.zeros((len(filelist_lintest[0]),2,8))
            for i in range(len(filelist_lintest[0])):
                ldata[i] += np.load(os.path.join(_path,filelist_lintest[0][i]))['global_median']
            ldata = ldata.T

            DRz = ldata[line][column]/ldata[0][0] * norm

            # py.title('%i x %i' % (column+1,line+1))
            #
            # py.plot(ldata[line][column],DRz,'o')
            # py.show()
            # continue

            if not config[narr]['fit']:
                narr+=1
                lincorr[column][line]['type'] = 0
                print 'skipping array %i...' % narr
                continue


            heaviside = lambda x,x0,t : 1 / (1+np.exp(-(x-x0)/t))
            if config[narr]['type'] == 1:
                start = float(config[narr]['start'])
                mid = float(config[narr]['stop'])
                stop = float(config[narr]['stop'])
            else:
                start = float(config[narr]['start'])
                mid = float(config[narr]['mid'])
                stop = float(config[narr]['stop'])

            mask = np.bitwise_and(ldata[line][column] > start,
                                  ldata[line][column] < mid)
            print start,mid,stop, len(mask[mask])
            c = np.polyfit(ldata[line][column][mask], DRz[mask],2)

            if config[narr]['type'] == 1:
                lincorr[column][line]['type'] = 1
                lincorr[column][line]['c1_1'] = c[0]
                lincorr[column][line]['c1_2'] = c[1]
                lincorr[column][line]['c1_3'] = c[2]
                py.subplot(211)
                py.plot(ldata[line][column][mask],DRz[mask],'o')
                xx = np.arange(np.min(ldata),np.max(ldata),1000)
                p = np.poly1d(c)
                py.plot(xx,p(xx),'-')

                py.subplot(212)
                py.plot(ldata[line][column][mask],DRz[mask]-p(ldata[line][column][mask]),'o')

                # py.show()
                narr+=1
                continue

            nmask = np.bitwise_and(ldata[line][column] > mid,
                                   ldata[line][column] < stop)

            step = np.mean(ldata[line][column][nmask][1:]-ldata[line][column][nmask][:-1])


            c = np.polyfit(ldata[line][column][mask], DRz[mask],1)
            c2 = np.polyfit(ldata[line][column][nmask], DRz[nmask],4)

            nmask2 = np.bitwise_and(ldata[line][column] >  start,
                                    ldata[line][column] < stop)

            from scipy.optimize import leastsq

            def fitfunc(x,y):
                return (x[0]+x[1]*y)*(1.-heaviside(y,x[2],x[3])) + (x[4]+x[5]*y+x[6]*y**2.+x[7]*y**3+x[8]*y**4)*heaviside(y,x[2],x[3])
                # return (x[0]+x[1]*y)*(1.-heaviside(y,x[2],x[3])) + (x[4]+x[5]*y+x[6]*y**2.)*heaviside(y,x[2],x[3])

            def errfunc(par,x,y):
                return fitfunc(par,x) - y

            p0 = [c[1],c[0],15.5e3,step,c2[4],c2[3],c2[2],c2[1],c2[0]]
            # p0 = [c[1],c[0],15.5e3,step,c2[2],c2[1],c2[0]]

            coefs = leastsq(errfunc,p0,args=(ldata[line][column][nmask2],DRz[nmask2]))
            lincorr[column][line]['type'] = 2
            lincorr[column][line]['c1_1'] = coefs[0][0]
            lincorr[column][line]['c1_2'] = coefs[0][1]
            lincorr[column][line]['break'] = coefs[0][2]
            lincorr[column][line]['step'] = coefs[0][3]
            lincorr[column][line]['c2_1'] = coefs[0][4]
            lincorr[column][line]['c2_2'] = coefs[0][5]
            lincorr[column][line]['c2_3'] = coefs[0][6]
            lincorr[column][line]['c2_4'] = coefs[0][7]
            lincorr[column][line]['c2_5'] = coefs[0][8]


            print coefs
            py.subplot(211)
            py.plot(ldata[line][column][nmask2],DRz[nmask2],'o')
            xx = np.arange(np.min(ldata),np.max(ldata),1000)
            py.plot(xx,fitfunc(coefs[0],xx),'-')

            py.subplot(212)
            py.plot(ldata[line][column][nmask2],DRz[nmask2]-fitfunc(coefs[0],ldata[line][column][nmask2]),'o')

            # py.show()
            narr+=1

    np.save(os.path.join(_path,
                         'lincor_relative.npy'),
            lincorr)
    return

if __name__ == '__main__':
    main(sys.argv)