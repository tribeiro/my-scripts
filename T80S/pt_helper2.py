# coding=utf-8
import os
import numpy as np
import matplotlib.pyplot as plt
import ephem

pointings = 20
skip = 0  # Use this to skip N first pointings to resume a model session
altitude_min = 40
#altitude_max = 85
#azimuth_min = 5
#azimuth_max = 346

dec_min = -80.
dec_max = +19.
ah_min = -60. # in degrees
ah_max = +60. # in degrees

dec_grid = np.linspace(dec_min,dec_max,11)

obs_lat = "-30:10:04.31"
obs_long = "-70:48:20.48"
obs_elev = 2187

obs = ephem.Observer()
obs.lat = obs_lat
obs.long = obs_long
obs.elevation = obs_elev

n = 256

radius = np.sqrt(np.arange(n) / float(n))

golden_angle = np.pi * (3 - np.sqrt(5))
theta = golden_angle * np.arange(n)

points = np.zeros((n, 2))
points[:,0] = np.cos(theta)
points[:,1] = np.sin(theta)
points *= radius.reshape((n, 1))

# print points

# plt.scatter(points[:,0],points[:,1])
# plt.show()

# plt.clf()
#
#
# ax = plt.subplot(111, projection='polar')
#
# # ax.scatter(points[:,0],points[:,1]*180./np.pi)
# ax.set_theta_zero_location("N")


ss_alt = np.array([])
ss_az = np.array([])
ss_ah = np.array([])
ss_dec = np.array([])

for dec in dec_grid:
    alt_max = np.arcsin( np.sin(dec*np.pi/180.) * np.sin(obs.lat.real) + np.cos(dec*np.pi/180.) * np.cos(obs.lat.real))*180./np.pi
    print '-->',dec,np.cos(dec*np.pi/180.),np.cos((-alt_max+120)*np.pi/180),alt_max
    npts1 = np.ceil(8*np.cos((-alt_max+120)*np.pi/180))
    npts2 = np.ceil(8*np.cos(dec*np.pi/180))
    npts = np.ceil((npts1+npts2)/2.)
    if npts % 2:
        npts+=1
    ah_grid = np.linspace(ah_min+(90-alt_max),ah_max-(90-alt_max),npts) #np.cos(dec*np.pi/180.))

    # print dec, np.cos(theta)
    # sin(ALT) = sin(DEC)*sin(LAT)+cos(DEC)*cos(LAT)*cos(HA)
    #                 sin(DEC) - sin(ALT)*sin(LAT)
    # cos(A)   = ---------------------------------
    #                   cos(ALT)*cos(LAT)

    alt = np.arcsin( np.sin(dec*np.pi/180.) * np.sin(obs.lat.real) + np.cos(dec*np.pi/180.) * np.cos(obs.lat.real) * np.cos(ah_grid*np.pi/180.))

    az = np.arccos((np.sin(dec*np.pi/180.) - np.sin(alt)*np.sin(obs.lat.real)) / (np.cos(alt)*np.cos(obs.lat.real)))

    mask = np.sin(ah_grid) < 0
    az[mask] = 2.*np.pi - az[mask]

    mask_alt = alt>altitude_min*np.pi/180.
    # ax.plot(az[mask_alt] , 90 - alt[mask_alt] * 180./np.pi,'o')
    # print ah_grid
    # print dec

    ss_alt = np.append(ss_alt,alt[mask_alt])
    ss_az = np.append(ss_az,az[mask_alt])
    ss_ah = np.append(ss_ah,ah_grid[mask_alt])
    ss_dec = np.append(ss_dec,np.zeros_like(ah_grid[mask_alt])+dec)
    # ax.scatter(az[mask_alt] , 90 - alt[mask_alt] * 180./np.pi, color='r', alpha=1, s=20)
    # # # print dec
    # # # ax.scatter(ah_grid * np.pi / 180., np.zeros(10)+dec, color='r', alpha=1, s=20)
    # ax.set_yticklabels(90 - np.array(ax.get_yticks(), dtype=int))
    #
    # plt.plot(np.zeros(10)+dec,ah_grid,'.')

# exit()
map_points = np.array([ss_az*180./np.pi,ss_alt*180./np.pi,ss_ah,ss_dec]).T

# print map_points
# plt.show()
# exit()

plot = True
save_file = None  # 'dome_pointing.txt'  # None
load_file = None  # 'lna_dome_model_data.txt'  # None

use_starname = True # Use this if the method does not support pointing by chimera
use_mac_clipboard = False  # Will copy name of the stars to the clipboard. Only works on mac.
# LNA
# obs_lat = "-22:32:04"
# obs_long = "-45:34:57"
# obs_elev = 1864
# chimera_prefix = 'ssh lna'
# UFSC
# obs_lat = "-27:36:12.286"
# obs_long = "-48:31:20.535"
# obs_elev = 25
# T80S

chimera_prefix = 'ssh 150.162.131.89'

path = os.path.dirname(os.path.abspath(__file__))
star_catalogfile = os.path.join(path,'SAO.edb')

if use_starname:
    import ephem

    with open(star_catalogfile) as f:
        star_catalog = [ephem.readdb(l) for l in f.readlines()]


def get_nearby_star(catalog, alt, az):
    obs = ephem.Observer()
    obs.lat = obs_lat
    obs.long = obs_long
    obs.elevation = obs_elev
    dist = []
    for star in star_catalog:
        star.compute(obs)
        dist.append(np.sqrt((alt - star.alt.real) ** 2 + (az - star.az.real) ** 2))
    nearby_star = np.argmin(dist)
    print star_catalog[nearby_star].ra.real,star_catalog[nearby_star].dec.real
    return star_catalog[nearby_star], dist[nearby_star]

# Vogel's method to equally spaced points
# Ref: http://blog.marmakoide.org/?p=1
radius = np.sqrt(np.arange(pointings) / float(pointings)) * (ah_min - ah_max) + ah_max

golden_angle = np.pi * (3 - np.sqrt(5))
theta = golden_angle * np.arange(pointings)

# Change to [0-2pi] inteval
# theta = [angin2pi(a) for a in theta]
#
# map_points = np.zeros((pointings, 2))
# map_points[:, 0] = theta
# map_points[:, 0] *= 180 / np.pi
# map_points[:, 1] = radius
# Order by azimuth to avoid unecessary dome moves.
map_points = map_points[np.lexsort((map_points[:, 2], map_points[:, 3]))]

for i in range(len(map_points)):
    print map_points[i]

if load_file is not None:
    skip_too_close = list()
    # points_save = list()
    load_model = np.loadtxt(load_file).T[:2]
    for point_load in load_model.T:
        offset = 0
        for i in range(len(map_points)):
            map_point = map_points[i - offset]
            if np.sqrt((point_load[0] - map_point[0]) ** 2 + (point_load[1] - map_point[1]) ** 2) < 4:
                skip_too_close.append(map_point)
                map_points = np.delete(map_points, i, axis=0)
                offset += 1
    skip_too_close = np.array(skip_too_close)

if plot:
    plt.clf()
    ax = plt.subplot(111, projection='polar')
    ax.set_theta_zero_location("N")
    ax.scatter(map_points[:, 0] * np.pi / 180., 90 - map_points[:, 1], color='r', alpha=1, s=20)
    if load_file is not None:
        ax.scatter(load_model[0] * np.pi / 180., 90 - load_model[1], color='green', s=20)
        ax.scatter(skip_too_close[:, 0] * np.pi / 180., 90 - skip_too_close[:, 1], color='black', s=20)
        print 'Skip %d' % len(skip_too_close)
    ax.grid(True)
    ax.set_ylim(90 - altitude_min + 10, 0)
    ax.set_yticklabels(90 - np.array(ax.get_yticks(), dtype=int))
    # plt.show()
    plt.draw()

if save_file is not None:
    np.savetxt(save_file, map_points, fmt='%6.3f')

i = skip
dry = False
for point in map_points[skip:]:
    i += 1
    alt, az = point[1], point[0]
    print('Point: # %i (alt, az): %.2f %2f' % (i, alt, az))
    # If a star name is needed to the method of pointing model, get the nearest star from the desired point.
    if use_starname:
        star, distance = get_nearby_star(star_catalog, alt * np.pi / 180, az * np.pi / 180)
        alt, az = star.alt.real * 180 / np.pi, star.az.real * 180 / np.pi
        os.system('echo %s | pbcopy' % star.name)
        s = 'S'
        if not dry:
            s = raw_input('Point Telescope to star %s (ra, dec, alt, az, dist): %s, %s, %s, %s, %.2f and press ENTER to verify S to skip' % (
                star.name, star.ra, star.dec, star.alt, star.az, distance))

        if s == 'S':
            continue
    else:
        print('Pointing telescope...')
        # os.system('%s chimera-tel --slew --alt %.2f --az %2.f' % (chimera_prefix, alt, az))
        print '%s chimera-tel --slew --alt %.2f --az %2.f' % (chimera_prefix, alt, az)
    if plot:
        ax.scatter(point[0] * np.pi / 180, 90 - point[1], color='b', s=10)
        ax.set_title("%d of %d done" % (i - 1, pointings), va='bottom')
        plt.draw()
    print('Verifying pointing...')
    print('chimera-pverify --here')
    # os.system('%s chimera-pverify --here' % chimera_prefix)
    print '%s chimera-pverify --here' % chimera_prefix
    print('\a')  # Ring a bell when done.
    if not dry:
        raw_input('Press ENTER for next pointing.')

plt.show()