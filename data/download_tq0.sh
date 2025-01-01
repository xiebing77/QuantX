#!/bin/bash

#source ~/.profile


symbol=KQ.m@SHFE.rb
sec=300
#years=(2016 2017 2018 2019 2020 2021 2022 2023 2024)
years=(2022)

for year in ${years[*]}
do

    #echo $kline_type
    sleep 2
    echo "downloading   ${product}${date}"
    python3 download_tq0.py -symbol ${symbol} -sec ${sec} -year ${year}

done
