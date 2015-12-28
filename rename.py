#!/usr/bin/python2
# coding: utf-8

import sys, os

orig = sys.argv[1]
repl = sys.argv[2]

files = os.listdir('.')
cnt = 0

for f in files:
	if f.count(orig) > 0:
		cnt+=1
		os.rename(f, f.replace(orig, repl))

print 'Переименовано: %i' % cnt
