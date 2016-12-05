#!/bin/bash

brightness=`echo \`xbacklight -get\`/1 | bc`

if (( $brightness >= 1 ))
then
    xbacklight -set 0
else
    xbacklight -set 100
fi
