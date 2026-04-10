#!/bin/bash

#source ~/.profile



for filename in $(ls *.csv)
do
    echo ${filename}
    prefix=${filename%_*}
    #echo ${prefix}
    sed -i "" "s/${prefix}.//g" ${filename}
    sed -i "" "s/datetime,datetime_nano/datetime_str,datetime/g" ${filename}
    #sed -i "" "s/datetime_nano/datetime/g" ${filename}
done
