#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#
# Copyright 2015 (CEFCA)
# Authors: Jesus Varela
#
# This file is part of JPAS pipeline jype
#
# jype is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jype is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with JPAS Pipeline. If not, see <http://www.gnu.org/licenses/>.
#
######################################################################
#
# Description:
#
#   Script to generate lists of pointings following a simple grid pattern.
#
# Known issues:
#
# TODO:
#    * Option to read an already existing file of pointings.
#
# Notes:
#
#
# Examples:
#
#   J-PLUS pointing list:
#       import JPLUS_Pointings as jplus_p
#       jplus_pointings = jplus_p.PointingsMap()
#       jplus_pointings.make_pointings()
#       jplus_pointings.save_pointings("Pointings_JPLUS.tab")
#       jplus_pointings.plot_tan()   # To produce a plot
#       savefig("JPLUS_Pointings.png")
#
#
######################################################################

import numpy as np
import os
import pylab as plt
import sys
import datetime

FoV = {}

FoV['t80cam'] = {
    'width' : 0.555*9216./3600.,  # 1.42 deg
    'height' : 0.555*9232./3600.
    }
FoV['Pathfinder'] = {
    'width' : 0.227*9216./3600.,
    'height' : 0.227*9232./3600.
    }

Pixsize = { 't80cam' : 0.556,
            'Pathfinder' : 0.2267
            }

SurveyLimits = []

#
# Northern Area
#
SurveyLimits.append(
    {
    'ra_min' : 7.*15.,
    'ra_max' : (17.+40/60.)*15.,
    'dec_min' : 20.,
    'dec_max' : 80
    }
)


SurveyLimits.append({
    'ra_min' : (17.+40/60.)*15.,
    'ra_max' : 19.*15.,
    'dec_min' : 30.,
    'dec_max' : 80
    }
)
#
# Southern Area
#
SurveyLimits.append({
    'ra_min' : 0.,
    'ra_max' : (2.+50/60.)*15.,
    'dec_min' :-3.,
    'dec_max' : 8
    }
)

SurveyLimits.append({
    'ra_min' : 0.,
    'ra_max' : (2.+10/60.)*15.,
    'dec_min' : 8.,
    'dec_max' : 10.
    }
)

SurveyLimits.append({
    'ra_min' : -2.*15,
    'ra_max' : (2.+10/60.)*15.,
    'dec_min' : 10.,
    'dec_max' : 27.
    }
)

SurveyLimits.append({
    'ra_min' : -2.*15,
    'ra_max' : (2.+40/60.)*15.,
    'dec_min' : 27.,
    'dec_max' : 35.
    }
)

SurveyLimits.append({
    'ra_min' : 0.,
    'ra_max' : (2.+40/60.)*15.,
    'dec_min' : 35.,
    'dec_max' : 46.
    }
)


class PointingsMap(object):

    def __init__(self,
                 delta_dec=None,
                 delta_ra=None,
                 camera='t80cam',
                 overlap_pix_dec=200.,
                 overlap_pix_ra=200.):

        self.delta_dec=delta_dec
        self.delta_ra=delta_ra
        self.camera=camera
        self.overlap_pix_dec=overlap_pix_dec
        self.overlap_pix_ra=overlap_pix_ra

        if not self.delta_dec:
            self.delta_dec = FoV[self.camera]['height']-self.overlap_pix_dec*Pixsize[camera]/3600.
            # This is the offset in degrees not in coordinates
            # To compute the offset in coordinates is needed to divide
            # by cos(dec)
            self.delta_ra = FoV[self.camera]['width']-self.overlap_pix_ra*Pixsize[camera]/3600.

    def make_pointings(self):
        '''Generate the pointings.

        '''

        self.pointings = {'dec':[],
                          'ra':[]
                          }
        # For northern area ("poncho")
        for _dec in np.arange(20+self.delta_dec/2.,80.1-self.delta_dec/2.,self.delta_dec):
            # The step between adjacent pointings is measured along the "southern"
            # border.
            _delta_ra = self.delta_ra/np.cos(np.radians(_dec-np.sign(_dec)*self.delta_dec/2.))
            # Note: The upper value of RA is a bit larger than the limit to avoid
            #       rounding problems.
            for _ra in np.arange(7.*15+_delta_ra/2.,19.1*15-_delta_ra/2.,_delta_ra):
                if check_inside_survey(_ra,_dec):
                    self.pointings['dec'].append(_dec)
                    self.pointings['ra'].append(_ra)
        #
        # For southern area ("camiseta")
        #

        # Blocks separated by their initial RA
        for _dec in np.arange(-3+self.delta_dec/2.,8,self.delta_dec):
            # The step between adjacent pointings is measured along the "northern"
            # border.
            _delta_ra = self.delta_ra/np.cos(np.radians(_dec-np.sign(_dec)*self.delta_dec/2.))
            for _ra in np.arange(0+_delta_ra/2.,3.1*15-_delta_ra/2.,_delta_ra):
                if check_inside_survey(_ra,_dec):
                    self.pointings['dec'].append(_dec)
                    self.pointings['ra'].append(_ra)


        _last_dec = _dec

        for _dec in np.arange(_dec+self.delta_dec,35,self.delta_dec):
            # The step between adjacent pointings is measured along the "northern"
            # border.
            _delta_ra = self.delta_ra/np.cos(np.radians(_dec-np.sign(_dec)*self.delta_dec/2.))
            for _ra in np.arange(-2.*15+_delta_ra/2.,3.1*15-_delta_ra/2.,_delta_ra):
                if check_inside_survey(_ra,_dec):
                    self.pointings['dec'].append(_dec)
                    self.pointings['ra'].append(_ra)


        for _dec in np.arange(_dec+self.delta_dec,46.1-self.delta_dec/2.,self.delta_dec):
            # The step between adjacent pointings is measured along the "northern"
            # border.
            _delta_ra = self.delta_ra/np.cos(np.radians(_dec-np.sign(_dec)*self.delta_dec/2.))
            for _ra in np.arange(0+_delta_ra/2.,3.1*15-_delta_ra/2.,_delta_ra):
                if check_inside_survey(_ra,_dec):
                    self.pointings['dec'].append(_dec)
                    self.pointings['ra'].append(_ra)

    def save_pointings(self,output='pointings.tab'):
        '''

        '''
        f = open(output,'w')

        f.write(
            "################################################\n"
            "#               J-PLUS Pointings\n"
            "################################################\n"
            "#\n"
            "# Author : Jesus Varela (jvarela@cefca.es)\n"
            "# Date: {0}\n".format(datetime.date.today().isoformat())+
            "# Camera: {0}\n".format(self.camera)+
            "# Width of FoV [deg]: {0}\n".format(FoV[self.camera]['width'])+
            "# Height of FoV [deg]: {0}\n".format(FoV[self.camera]['height'])+
            "# Offset(RA): {0}\n".format(self.delta_ra)+
            "# Offset(DEC): {0}\n".format(self.delta_dec)+
            "#\n"
            "# ID   RA[deg]  DEC[deg]\n"
            )

        for n,r in enumerate(self.pointings['ra']):
            f.write("{2:4.0f}  {0:.4f}  {1:.4f}\n".format(self.pointings['ra'][n],self.pointings['dec'][n],n+1))

        f.close()

    def plot_tan(self,
                 ra_center=None,ra_width=None,
                 dec_center=None,dec_width=None,
                 show_coords=False,
                 show_area='north'):

        fig = plt.figure("J-PLUS Survey Strategy - Tangential")

        fig.clf()

        ax = fig.add_subplot(111)

        _ra = 'ra'
        _dec = 'dec'

        if show_area in ['north','all','both']:
            ax.scatter((self.pointings[_ra]),
                       (self.pointings[_dec]),
                       color='red',
                       s=4)
        
#        if show_area in ['south','all','both']:
#            ax.scatter((self.points_south[_ra]),
#                       (self.points_south[_dec]),
#                       color='blue')

        self.pointings['rot'] = np.array(self.pointings[_ra])*0.

        # This computation is needed because the rotation is not around
        # the center but aroung the lower left angle.
        _l = np.sqrt(FoV[self.camera]['height']**2+(FoV[self.camera]['width']/np.cos(np.radians(self.pointings[_dec])))**2)/2.
        _theta = np.arctan((FoV[self.camera]['width']/np.cos(np.radians(self.pointings[_dec])))/FoV[self.camera]['height'])
        _dyc = _l*np.cos(np.pi-_theta+np.radians(self.pointings['rot']))
        _yc = self.pointings[_dec] + _dyc
        _dxc = _l*np.sin(np.pi-_theta+np.abs(np.radians(self.pointings['rot'])))#/np.cos(np.radians(_yc))
        _xc = self.pointings[_ra] - _dxc
        self._yc = _yc
        self._xc = _xc
        self._dyc = _dyc
        self._dxc = _dxc
        _xwidth = FoV[self.camera]['width']/np.cos(np.radians(self.pointings[_dec]))
        _yheight = FoV[self.camera]['height']+_xc*0.
        _delta_zeta = np.array([-FoV[self.camera]['width'],-FoV[self.camera]['width'],FoV[self.camera]['width'],FoV[self.camera]['width'],-FoV[self.camera]['width']])/2.
        _delta_eta = np.array([-FoV[self.camera]['height'],FoV[self.camera]['height'],FoV[self.camera]['height'],-FoV[self.camera]['height'],-FoV[self.camera]['height']])/2.

        # Computing and plotting the position of the vertices of the FoV
        for n,c in enumerate(self.pointings[_ra]):

            alpha_vert = []
            delta_vert = []

            alpha_0 = self.pointings[_ra][n]
            delta_0 = self.pointings[_dec][n]

            for _n,x in enumerate(_delta_zeta):
                #print "_n=",_n
                zeta = np.radians(_delta_zeta[_n])
                eta = np.radians(_delta_eta[_n])

                tan_delta_alpha = zeta/(np.cos(np.radians(delta_0))-eta*np.sin(np.radians(delta_0)))
                sin_delta = (np.sin(np.radians(delta_0))+eta*np.cos(np.radians(delta_0)))/(np.sqrt(1+eta*eta+zeta*zeta))
                alpha = np.degrees(np.arctan(tan_delta_alpha))+alpha_0
                delta = np.degrees(np.arcsin(sin_delta))
                if show_coords:
                    ax.text(alpha,delta,"{0:.4f},{1:.4f}".format(alpha,delta),angle=45,fontsize='xx-small'),
                alpha_vert.append(alpha)
                delta_vert.append(delta)

            ax.plot(alpha_vert,delta_vert,color='blue')

        ax.set_ylim(-10,90)

        if ra_center:
            ax.set_xlim(ra_center-ra_width/2.,ra_center+ra_width/2.)

        if dec_center:
            ax.set_ylim(dec_center-dec_width/2.,dec_center+dec_width/2.)

        ax.set_xlabel("RA [deg]",fontsize='xx-large')
        ax.set_ylabel("DEC [deg]",fontsize='xx-large')


def check_inside_survey(ra,dec):
    '''Function to check whether a point is within the limits
    of J-PAS

    '''

    is_inside = False
    for l in SurveyLimits:
        if (l['ra_min'] <= ra <= l['ra_max']) and (l['dec_min'] <= dec <= l['dec_max']):
             is_inside = True
             break

    return is_inside

def measure_jpas_area(npoints=1e7):
    '''Monte Carlo method to estimate the total area covered by J-PAS.

    '''

    ra_rand = np.random.random_sample(npoints)*360
    dec_rand=np.random.random(npoints)*180.-90
    cos_dec=np.cos(np.radians(dec_rand))
    test=np.random.random(npoints)

    dec_rand_sel = dec_rand[test<np.abs(cos_dec)]
    ra_rand_sel = ra_rand[test<np.abs(cos_dec)]

    print "Please, wait, this will take a while..."
    inside = [ check_inside_survey(x,y) for x,y in np.transpose([ra_rand_sel,dec_rand_sel]) ]

    print "Total area covered by J-PAS: {0:.0f} deg^2".format(np.sum(inside)*1./len(inside)*41253) 


if __name__ == '__main__':

    pass
