#!/bin/bash

FILE=`date +"Screenshot-%Y-%m-%d_%H-%M-%S".png`
HOST="slasyz.ru"
DESTINATION="$HOME/Pictures/screenshots"
DATE=`date "+%Y/%m/%d %H:%M:%S"`
#PASSWORD=`cat $HOME/.config/slasyz_ru/upload_password.txt`

env PATH=$PATH:/home/sl/Documents/bin/slop /home/sl/Documents/bin/maim/maim -s -b1 $DESTINATION/$FILE;
scp "$DESTINATION/$FILE" slasyz.ru:~/www/files.slasyz.ru/screenshots;
URL="http://files.slasyz.ru/$FILE"
#URL=`curl -b csrftoken=$csrf_token -F csrfmiddlewaretoken=$csrf_token -F fileup=@$DESTINATION/$FILE -F password=$PASSWORD $HOST/upload/upload-ajax/ | grep "success-file" | grep -Po "(?<=href=\").+(?=\")"` ;

echo $URL;
echo -n $URL | xclip -i;
echo "[1;32m$DATE[0m: [[1;33m$FILE[0m] $URL" >> ~/.simploader.log
exec kdialog --inputbox "Here is your link" "$URL";
