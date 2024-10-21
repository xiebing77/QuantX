#!/bin/bash

#source ~/.profile


symbol=SHFE.rb
#codes=(1605 1610 1701 1705 1710 1801 1805 1810 1901 1905 1910 2001 2005 2010 2101 2105 2110 2201 2205 2210 2301 2305 2310 2401 2405 2410)
codes=(2501)
#sec=300
sec=86400

for code in ${codes[*]}
do

    #echo $kline_type
    sleep 2
    echo "downloading   ${symble}"
    python3 download_tq_to_csv.py -symbol ${symbol} -sec ${sec} -code ${code}

done
