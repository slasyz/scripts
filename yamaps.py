#!/usr/bin/python
# coding: utf-8

import sys
from urllib import quote
from urllib2 import urlopen, HTTPError
from xml.dom.minidom import parseString

if len(sys.argv) < 2:
    print(u'Недостаточно параметров.\n./yamaps.py OBJECT')
    exit()

API_KEY = 'AOcWCkwBAAAAHtxYBAQA-dHgCyJmgoQi5nla9n1EU5mzB6UAAAAAAAAAAADIkjLbzu5uacEGjlf6Lu2MrAb-UA=='
OBJECT = ' '.join(sys.argv[1:])

def get_coordinats(query):
    xml = urlopen(u'http://geocode-maps.yandex.ru/1.x/?geocode=%s&key=%s' % (quote(query), API_KEY)).read()
    obj = parseString(xml)
    return obj.getElementsByTagName('pos')[0].childNodes[0].data.split(' ') # Долгота, широта

if __name__ == '__main__':
    try:
        long, lat = get_coordinats(OBJECT)
        print(u'Object "%s":\nLong: %s;\nLat: %s.' % (OBJECT.decode('UTF-8'), long, lat))
    except IndexError:
        print(u'Object "%s" not found.' % OBJECT.decode('UTF-8'))
    except KeyboardInterrupt:
        print(u'Exit by Ctrl+C.')
    except HTTPError:
        print(u'HTTP Error!')
