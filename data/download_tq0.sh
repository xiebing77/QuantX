#!/bin/bash

#source ~/.profile


symbol=KQ.m@SHFE.cu
years=(2017 2018 2019 2020 2021 2022)

for year in ${years[*]}
do

    #echo $kline_type
    echo "downloading   ${product}${date}"
    python3 download_tq0.py -symbol ${symbol} -year ${year}

done
