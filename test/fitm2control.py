import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from scipy.optimize import leastsq
import pylab as py

path = '/Users/tiago/Documents/m2controllaw_table4_051.fits'

hdu = fits.open(path)

GX = np.cos(hdu[1].data['ALT'] * np.pi / 180.)*np.sin(hdu[1].data['AZ'] * np.pi / 180.)
GY = np.cos(hdu[1].data['ALT'] * np.pi / 180.)*np.cos(hdu[1].data['AZ'] * np.pi / 180.)
GZ = np.sin(hdu[1].data['ALT'] * np.pi / 180.)
T = hdu[1].data['TubeRod']

data = hdu[1].data['Z']

def fitfunc(p,coords):
    x,y,z,t = coords[0],coords[1],coords[2],coords[3]
    return p[0] + p[1] * x + p[2] * y + p[3] * z + p[4] * t + p[5] * t * t

errfunc = lambda p, x: fitfunc(p, x) - x[4]

p0 = np.zeros(6)+1.e-1

ct = np.polyfit(T,data,2)

p0[0] = ct[0]
p0[-2] = ct[1]
p0[-1] = ct[2]

p1, flag = leastsq(errfunc, p0, args=([GX,GY,GZ,T,data],))

print p0
print p1
print ct

xx = np.linspace(np.min(T),np.max(T))
yy = np.poly1d(ct)


# make these smaller to increase the resolution
dx, dy = 0.5*np.pi/180., 0.5*np.pi/180.

# generate 2 2d grids for the x & y bounds
y, x = np.mgrid[slice(np.pi/6, np.pi/2. + dx, dx),
                slice(0, 2*np.pi + dy, dy)]
# x and y are bounds, so z should be the value *inside* those bounds.
# Therefore, remove the last value from the z array.

# GZ
z = fitfunc(p1,(np.cos(y)*np.sin(x),np.cos(y)*np.cos(x),np.sin(y),np.zeros_like(y)+9.))
z = z[:-1, :-1]
z_min, z_max = z.min(), np.abs(z).max()
print z_max,z_min
ax = plt.subplot(111, projection='polar')

ax.set_theta_zero_location("N")

# plt.subplot(1, 1, 1, polar=True)
plt.pcolormesh(x, 90.-y*180./np.pi, z, cmap='RdBu', vmin=z_min, vmax=z_max)
plt.colorbar()
plt.scatter( hdu[1].data['AZ']* np.pi / 180., 90 - hdu[1].data['ALT'], color='b', s=10)

ax.grid(True)
ax.set_ylim(90, 0)
ax.set_yticklabels(90 - np.array(ax.get_yticks(), dtype=int))

plt.show()