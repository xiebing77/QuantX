#!/bin/bash

#source ~/.profile
range=$1
echo $range

mds=(binance_spot)
echo ${mds[*]}

symbles=btc_usdt,eth_usdt,bnb_usdt
echo ${symbles}

kline_types=5m,15m,30m,1h,2h,4h,6h,8h,12h,1d
echo ${kline_types}

for md in ${mds[*]}
do

    #echo $kline_type
    echo "downloading  ${range}  ${md}"
    if [ $range ]
    then
        python3 download.py -source $md -symbols $symbles -kts $kline_types -range $range
    else
        python3 download.py -source $md -symbols $symbles -kts $kline_types
    fi

done
