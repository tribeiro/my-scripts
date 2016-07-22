#!/usr/bin/env python

import json
import re

import requests

import xml.etree.ElementTree as ET

# from bs4 import BeautifulSoup


# http://telops.lcogt.net/dajaxice/netnode.refresh/
import time


class LCOGTScrapper(object):

    def scrape(self):

        self.client = requests.session()

        self.a = self.client.get('http://telops.lcogt.net/#')

        latest_comet_queue_id  = int(re.findall('Telops.latest_comet_queue_id = (.+);', self.a.text)[0])
        print latest_comet_queue_id
        self.r = self.client.post(
            url='http://telops.lcogt.net/dajaxice/netnode.refresh/',
            data={'argv': json.dumps({"latest": latest_comet_queue_id})},
            headers={
                'Accept': '*/*',
                'Accept-Encoding':'gzip, deflate',
                "Content-Type": "application/x-www-form-urlencoded",
                'Host': 'telops.lcogt.net',
                "Origin": "http://telops.lcogt.net",
                "Referer": "http://telops.lcogt.net/",
                'X-CSRFToken': None,
                'X-Requested-With': 'XMLHttpRequest',

            },
            cookies = {'pushstate':'pushed'}

        )

        return json.loads(self.r.text)


c = LCOGTScrapper()
data = c.scrape()

for val in data:
    if 'id' in val.keys():
        # print 'id', val['id']
        if val['id'] == '#site-lsc-ssb-system-Weather-tip':
            print val


