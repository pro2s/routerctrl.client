#!/bin/ash
result=$(wget -qO- http://router.pro2s.ru/online)
echo $result
if [[ $result -lt "700" ]] && [[ $result -gt "0" ]];
then
    echo "run update script"
    /root/router.py
fi 


 
