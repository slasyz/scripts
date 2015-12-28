#!/bin/bash

brightness=`echo \`xbacklight -get\`/1 | bc`

if (( $brightness >= 99 ))
then
    xbacklight -set 10
elif (( $brightness >= 49 ))
then
    xbacklight -set 100
elif (( $brightness >= 9 ))
then
    xbacklight -set 50
fi

