#!/usr/bin/python2
# coding: utf-8

# Translate phrases via Google Translate.

import sys, json, re
from urllib import quote
from urllib2 import urlopen, HTTPError, Request

class WrongLanguage(Exception): pass

if len(sys.argv) < 3:
	print(u'Not enough parameters.\n./translate.py ORIGIN_LANG DEST_LANG TEXT')
	exit()

def transl(string, l1, l2):
	#res = json.loads(urlopen('http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&q=%s&langpair=%s%%7C%s' % (quote(TEXT), LANG1, LANG2)).read())
	#url = 'http://translate.google.com/translate_a/t?text=%s&sl=%s&tl=%s&client=t&hl=en&multires=0' % (quote(string), l1, l2)
	url = 'https://translate.google.ru/translate_a/single?client=t&sl=%s&tl=%s&hl=ru&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=at&ie=UTF-8&oe=UTF-8&otf=1&srcrom=0&ssel=0&tsel=0&kc=1&tk=521222|589012&q=%s' % (l1, l2, quote(string))
	request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	res = urlopen(request).read()
	res = re.sub(r',{2,}', ',', res).replace(',]', ']').replace('[,', '[')
	res = json.loads(res)
	return res[0][0][0]


def main():
	LANG1, LANG2 = sys.argv[1:3]
	TEXT = ' '.join(sys.argv[3:])
	if (len(LANG1) != 2) or (len(LANG2) != 2):
		raise WrongLanguage()

	for s in TEXT.split('\n'):
		if s != '':
			print transl(s, LANG1, LANG2)
		else:
			print '';
	
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print(u'Exit by Ctrl+C.')
	#except IndexError:
	#	print(u'Translation is impossible.')
	except WrongLanguage:
		print(u'Wrong language.')
	#except HTTPError:
	#	print(u'HTTP Error!')

