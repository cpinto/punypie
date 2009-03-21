# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4

"""puny.py is a library for the URL shortener service created by SAPO

"""

import urllib,urllib2
import re
import unittest

__all__ = ['shorten','expand','PunyURL']
__author__ = 'Celso Pinto'
__email__ = 'cpinto@yimports.com'

TO_PUNY = 'http://services.sapo.pt/PunyURL/GetCompressedURLByURL'
FROM_PUNY = 'http://services.sapo.pt/PunyURL/GetURLByCompressedURL'

puny_match = re.compile(r'<puny>(http.*)</puny>').search
ascii_match = re.compile(r'<ascii>(http.*)</ascii>').search
preview_match = re.compile(r'<preview>(http.*)</preview>').search
url_match = re.compile(r'<url><!\[CDATA\[(http.*)\]\]></url>').search

class PunyURL(object):
    puny = None
    ascii = None
    preview = None
    url = None

def _process_response(s):
    puny_url = PunyURL()
    puny_url.puny = puny_match(s).group(1)
    puny_url.ascii = ascii_match(s).group(1)
    puny_url.preview = preview_match(s).group(1)
    puny_url.url = url_match(s).group(1)
    return puny_url

def shorten(url):
    ''' Shorten a URL

        Returns a PunyURL object with the shortened versions of the URL.
        Example usage:
        >>> import puny
        >>> puny = puny.shorten('http://developers.sapo.pt')
        >>> print puny.puny
        http://漭.sl.pt
        >>> print puny.ascii
        http://b.ot.sl.pt
    '''
    u = '?'.join((TO_PUNY,urllib.urlencode({'url':url})))
    return _process_response(urllib2.urlopen(u).read())

def expand(puny):
    ''' Expand a puny URL to the original URL
        
        Returns the original URL
        Example usage:
        >>> import puny
        >>> print puny.expand('http://b.ot.sl.pt')
        http://developers.sapo.pt
    '''
    u = '?'.join((FROM_PUNY,urllib.urlencode({'url':puny})))
    puny_url = _process_response(urllib2.urlopen(u).read())
    return puny_url.url

class PunyTests(unittest.TestCase):
    def testToPunyResponseHandling(self):
        puny = _process_response('''<?xml version="1.0" encoding="utf-8"?>
        <punyURL xmlns="http://services.sapo.pt/Metadata/PunyURL">
            <puny>http://漭.sl.pt</puny>
            <ascii>http://b.ot.sl.pt</ascii>
            <preview>http://b.ot.sl.pt/-</preview>
            <url><![CDATA[http://developers.sapo.pt/]]></url>
        </punyURL>''')

        self.failUnlessEqual(puny.puny,'http://漭.sl.pt')
        self.failUnlessEqual(puny.ascii,'http://b.ot.sl.pt')
        self.failUnlessEqual(puny.preview,'http://b.ot.sl.pt/-')
        self.failUnlessEqual(puny.url,'http://developers.sapo.pt/')

    def testFromPunyResponseHandling(self):
        puny = _process_response('''<?xml version="1.0" encoding="utf-8"?>
        <punyURL xmlns="http://services.sapo.pt/Metadata/PunyURL">
            <puny>http://漭.sl.pt</puny>
            <ascii>http://b.ot.sl.pt</ascii>
            <preview>http://b.ot.sl.pt/-</preview>
            <url><![CDATA[http://developers.sapo.pt/]]></url>
        </punyURL>''')

        self.failUnlessEqual(puny.url,'http://developers.sapo.pt/')

    def testRemoteToPunyResponse(self):
        puny = shorten('http://developers.sapo.pt/')

        self.failUnlessEqual(puny.puny,'http://漭.sl.pt')
        self.failUnlessEqual(puny.ascii,'http://b.ot.sl.pt')
        self.failUnlessEqual(puny.preview,'http://b.ot.sl.pt/-')
        self.failUnlessEqual(puny.url,'http://developers.sapo.pt/')

    def testRemoteFromPunyResponse(self):
        self.failUnlessEqual(expand('http://漭.sl.pt'),'http://developers.sapo.pt/')
        self.failUnlessEqual(expand('http://b.ot.sl.pt'),'http://developers.sapo.pt/')

if __name__ == '__main__':
    unittest.main()
