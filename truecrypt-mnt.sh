#!/bin/bash

if [ -a /media/truecrypt/stuff ] 
then
	exec truecrypt -d /media/truecrypt
else
	exec truecrypt /home/sl/Documents/private.txt /media/truecrypt
fi
