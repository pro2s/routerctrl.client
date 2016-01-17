#!/bin/ash
ENV=/root/.profile
result=$(wget -qO- http://router.pro2s.ru/online)
minutes=$( date +%M )
test=$((minutes%5))
start=false 
echo "$result"

[ ! -f /root/online ] && echo "-1" > /root/online
OLD_ONLINE=$(cat /root/online)
echo "$OLD_ONLINE"

if [[ "$result" -lt "$OLD_ONLINE" ]] && [[ "$OLD_ONLINE" -gt "300" ]];
then
    start=true
fi 
if [[ "$result" -gt "0" ]] && [[ "$OLD_ONLINE" -lt "0" ]];
then
    start=true 
fi
if [[ $test = "0" ]] && [[ $result -lt "600" ]] && [[ $result -gt "0"]];
then
    start=true
fi

if [ "$start" = true ] ; then
    echo "run update script"
    /root/router.py
fi

echo $result > /root/online

 
