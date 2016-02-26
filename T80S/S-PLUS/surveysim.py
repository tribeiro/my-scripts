#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# chimera - observatory automation system
# Copyright (C) 2006-2007  P. Henrique Silva <henrique@astro.ufsc.br>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import sys,os
from datetime import datetime,timedelta
from dateutil import tz
from chimera.core.manager import Manager
from t80sched.scheduler.model import Session, ObsBlock
import logging
import subprocess

logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=logging.DEBUG)

def main(argv):

    '''
    This script is designed for testing scheduling algorithms on chimera. It will, in its task, use the standard
    databases which may cause loss of information. When simulating surveys, use a separate chimera instance far away
    from any instance used on real case scenarios.

    :param argv:
    :return:
    '''

    manager = Manager()
    site = manager.getProxy('127.0.0.1:7666/Site/0')
    surveyDay = datetime(2015,1,1).replace(tzinfo=tz.tzutc())

    cmdlist = ['chimera-t80sched --makeQ --pid SPLUS --jdstart %f --jdend %f',
               'chimera-t80sched --makeQ --pid EXTMONI --jdstart %f --jdend %f']

    for i in range(2):

        sunset = site.sunset_twilight_end(surveyDay)
        nigthStart = site.JD(sunset)
        nigthEnd = site.JD(site.sunrise_twilight_begin(sunset))

        session = Session()
        blockList = session.query(ObsBlock).filter(ObsBlock.observed == False,ObsBlock.pid == 'SPLUS')

        todoBlocks = blockList.count()

        logging.info('%i blocks to observe'% todoBlocks)
        logging.debug('Night start: %s'% nigthStart)
        logging.debug('Night end: %s'% nigthEnd)
        logging.debug('Night time: %.2f h'%((nigthEnd-nigthStart)*24.))

        for cmd in cmdlist:
            logging.debug(cmd% (nigthStart,nigthEnd))
            subprocess.check_call([cmd% (nigthStart,nigthEnd)],
                                  shell=True)

        surveyDay+=timedelta(days=1)

    return 0


if __name__ == '__main__':
    main(sys.argv)