# coding=utf-8
import os
import numpy as np
import ephem
import matplotlib
# matplotlib.use('GTKAgg')
import matplotlib.pyplot as plt


pointings = 20
skip = 0  # Use this to skip N first pointings to resume a model session
altitude_min = 42.5
#altitude_max = 85
#azimuth_min = 5
#azimuth_max = 346

dec_min = -80.
dec_max = +19.

dec_grid = np.linspace(dec_min,dec_max,21)

obs_lat = "-30:10:04.31"
obs_long = "-70:48:20.48"
obs_elev = 2187

obs = ephem.Observer()
obs.lat = obs_lat
obs.long = obs_long
obs.elevation = obs_elev

ah_grid = np.zeros(len(dec_grid))

dec = dec_grid

alt = np.arcsin( np.sin(dec*np.pi/180.) * np.sin(obs.lat.real) + np.cos(dec*np.pi/180.) * np.cos(obs.lat.real) * np.cos(ah_grid*np.pi/180.))
az = np.ma.fix_invalid(np.arccos((np.sin(dec*np.pi/180.) - np.sin(alt)*np.sin(obs.lat.real)) / (np.cos(alt)*np.cos(obs.lat.real))),
                       fill_value=0.)

mask_dec = np.bitwise_and(az.mask,dec*np.pi/180. < obs.lat.real)

az[mask_dec] = np.pi

# ax.scatter(az.data , 90 - alt * 180./np.pi, color='r', alpha=1, s=20)

d_alt = alt - altitude_min*np.pi/180.
d_ah = d_alt * 12./np.pi

print d_alt*180./np.pi,d_ah

alt_arr = np.array([])
az_arr = np.array([])
lane_arr = np.array([])
dec_lane = 1

for i in range(len(dec_grid)):
    dec=dec_grid[i]
    alt = np.arcsin( np.sin(dec*np.pi/180.) * np.sin(obs.lat.real) + np.cos(dec*np.pi/180.) * np.cos(obs.lat.real))

    if alt < altitude_min*np.pi/180.:
        continue
    ah0 = np.arccos((np.sin(altitude_min*np.pi/180.)-np.sin(dec*np.pi/180.) * np.sin(obs.lat.real))/(np.cos(dec*np.pi/180.) * np.cos(obs.lat.real)))
    alt0 = np.arcsin( np.sin(dec*np.pi/180.) * np.sin(obs.lat.real) + np.cos(dec*np.pi/180.) * np.cos(obs.lat.real))
    az0 = np.arccos((np.sin(dec*np.pi/180.) - np.sin(alt0)*np.sin(obs.lat.real)) / (np.cos(alt0)*np.cos(obs.lat.real)))
    # print ah0,ah0*12./np.pi,np.sin(alt)
    # ah_grid = [altitude_min]
    # ah_grid = np.linspace(0,ah0,np.floor(d_ah[i]*4))*180./12.
    # print dec, np.floor(np.sin(np.pi/2. - (obs.lat.real- dec*np.pi/180.))*12)
    N = np.floor(np.cos(dec*np.pi/180.)*36)
    # N= 100
    # print dec,N,np.cos(dec*np.pi/180.),np.cos()
    # N = 5*N - 44
    # print N
    # print ah0*12/np.pi
    ah0 = 12.*np.pi/12.
    ah_grid = np.linspace(ah0,0,N)[:-1]*180./np.pi

    alt = np.arcsin( np.sin(dec*np.pi/180.) * np.sin(obs.lat.real) + np.cos(dec*np.pi/180.) * np.cos(obs.lat.real) * np.cos(ah_grid*np.pi/180.))
    az = np.ma.fix_invalid(np.arccos((np.sin(dec*np.pi/180.) - np.sin(alt)*np.sin(obs.lat.real)) / (np.cos(alt)*np.cos(obs.lat.real))),
                           fill_value=0.)
    # print az*180/np.pi
    # mask_dec = np.bitwise_and(az.mask,dec*np.pi/180. < obs.lat.real)
    #
    # az[mask_dec] = np.pi
    mask = alt >= altitude_min*np.pi/180.

    # ax.plot(az.data[mask] , 90 - alt[mask] * 180./np.pi, 'r.')#, alpha=1, s=20)
    # ax.plot(-az.data[mask] , 90 - alt[mask] * 180./np.pi, 'r.')#, alpha=1, s=20)
    # ax.scatter(-az.data , 90 - alt * 180./np.pi, color='b', alpha=1, s=20)
    alt_arr = np.append(alt_arr,alt[mask])

    #alt_arr = np.append(alt_arr,alt[mask])
    alt_arr = np.append(alt_arr,[alt0,])

    alt_arr = np.append(alt_arr,alt[mask][::-1])

    az_arr = np.append(az_arr,az[mask])

    if dec*np.pi/180. > obs.lat.real:
        az_arr = np.append(az_arr,[0,])
    else:
        az_arr = np.append(az_arr,[np.pi,])

    az_arr = np.append(az_arr,2.*np.pi-az[mask][::-1])

    lane_arr = np.append(lane_arr,np.zeros(len(az[mask])*2+1)+dec_lane)
    dec_lane+=1

print "Total number of pointings: %i" % len(az_arr)
print alt_arr.shape,az_arr.shape,lane_arr.shape
map_points = np.array([az_arr*180./np.pi,alt_arr*180./np.pi,lane_arr]).T

if False:
    plt.clf()
    ax = plt.subplot(111, projection='polar')
    ax.set_theta_zero_location("N")

    ax.plot(az_arr , 90 - alt_arr * 180./np.pi,'b-')
    ax.scatter(az_arr , 90 - alt_arr * 180./np.pi, color='r', alpha=1, s=10)
    #ax.scatter(2.*np.pi-az_arr , 90 - alt_arr * 180./np.pi, color='r', alpha=1, s=10)
    ax.set_ylim(90 - altitude_min + 10, 0)
    ax.set_yticklabels(90 - np.array(ax.get_yticks(), dtype=int))
    print d_ah

plot = True
save_file = None  # 'dome_pointing.txt'  # None
load_file = None  # 'lna_dome_model_data.txt'  # None

use_starname = True # Use this if the method does not support pointing by chimera
use_mac_clipboard = False  # Will copy name of the stars to the clipboard. Only works on mac.

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
    # print star_catalog[nearby_star].ra.real,star_catalog[nearby_star].dec.real
    return star_catalog[nearby_star], dist[nearby_star]


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
    # plt.ion()
    ax.set_theta_zero_location("N")
    ax.scatter(map_points[:, 0] * np.pi / 180., 90 - map_points[:, 1], color='r', alpha=1, s=20)
    if load_file is not None:
        ax.scatter(load_model[0] * np.pi / 180., 90 - load_model[1], color='green', s=20)
        ax.scatter(skip_too_close[:, 0] * np.pi / 180., 90 - skip_too_close[:, 1], color='black', s=20)
        print 'Skip %d' % len(skip_too_close)
    ax.grid(True)
    ax.set_ylim(90 - altitude_min + 10, 0)
    ax.set_yticklabels(90 - np.array(ax.get_yticks(), dtype=int))
    plt.show()
    plt.draw()

if save_file is not None:
    np.savetxt(save_file, map_points, fmt='%6.3f')

i = skip
dry = True
star_name = ''

ilane = 0
for point in map_points[skip:]:
    i += 1
    # print('Point: # %i (alt, az): %.2f %2f' % (i, alt, az))
    # If a star name is needed to the method of pointing model, get the nearest star from the desired point.
    if ilane != point[2]:
        ilane = point[2]
        print("Doing reference pointing...")
        star, distance = get_nearby_star(star_catalog,77. * np.pi / 180., 278. * np.pi / 180.)
        alt, az = star.alt.real * 180 / np.pi, star.az.real * 180 / np.pi
        os.system('echo %s | pbcopy' % star.name)
        s = raw_input('Point Telescope to star %s (ra, dec, alt, az, dist): %s, %s, %s, %s, %.2f and press ENTER to verify' % (
            star.name, star.ra, star.dec, star.alt, star.az, distance))

    s = 'S'
    alt, az = point[1], point[0]
    if use_starname:
        star, distance = get_nearby_star(star_catalog, alt * np.pi / 180, az * np.pi / 180)
        alt, az = star.alt.real * 180 / np.pi, star.az.real * 180 / np.pi
        os.system('echo %s | pbcopy' % star.name)
        # s = 'S'
        if star_name == star.name:
            print 'WARNING: Repeating last star %s' % star_name

        if not dry:
            s = raw_input('Point Telescope to star %s (ra, dec, alt, az, dist): %s, %s, %s, %s, %.2f and press ENTER to verify, S to skip or R for reference' % (
                star.name, star.ra, star.dec, star.alt, star.az, distance))
        else:
            print 'Point Telescope to star %s (ra, dec, alt, az, dist): %s, %s, %s, %s, %.2f' % (
                star.name, star.ra, star.dec, star.alt, star.az, distance)

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
    # print('Verifying pointing...')
    # print('chimera-pverify --here')
    # # os.system('%s chimera-pverify --here' % chimera_prefix)
    # print '%s chimera-pverify --here' % chimera_prefix
    print('\a')  # Ring a bell when done.
    if not dry and s == 'R':
        print("Doing reference pointing...")
        star, distance = get_nearby_star(star_catalog,77. * np.pi / 180., 278. * np.pi / 180.)
        alt, az = star.alt.real * 180 / np.pi, star.az.real * 180 / np.pi
        os.system('echo %s | pbcopy' % star.name)
        s = raw_input('Point Telescope to star %s (ra, dec, alt, az, dist): %s, %s, %s, %s, %.2f and press ENTER to verify' % (
            star.name, star.ra, star.dec, star.alt, star.az, distance))

    elif not dry:
        raw_input('Press ENTER for next pointing.')

plt.show()


plt.show()