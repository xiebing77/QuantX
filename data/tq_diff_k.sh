#!/bin/bash

#source ~/.profile


if [ $# -ne 2 ]; then
    echo "egg: $0 symble interval"
    exit 1
fi
symble=$1
interval=$2
#echo ${symble} ${interval}

for filename in $(ls ${symble}*_${interval}_book.csv)
do
    tqfilename=${filename/_book.csv/.csv}
    echo ${tqfilename}  "<--->"  ${filename}
    python3 diff_csv.py -source kuaiqi_futures -files ${tqfilename} ${filename}
done
