#!/bin/bash

#source ~/.profile



for filename in $(ls *.csv)
do
    echo ${filename}
    prefix=${filename%_*}
    #echo ${prefix}
    sed -i "" "s/${prefix}.//g" ${filename}
    sed -i "" "s/datetime,/datetime_str,/g" ${filename}
    sed -i "" "s/datetime_nano/datetime/g" ${filename}
done
