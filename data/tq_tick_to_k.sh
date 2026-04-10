#!/bin/bash

#source ~/.profile


if [ $# -ne 2 ]; then
    echo "egg: $0 symble interval"
    exit 1
fi
symble=$1
interval=$2
#echo ${symble} ${interval}

for filename in $(ls ${symble}*_tick.csv)
do
    #echo ${filename}
    python3 tick_to_kline.py -source kuaiqi_futures -interval ${interval} -files ${filename} --book
done
