#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "$0: <db_file>"
	exit 0
fi

# get list of all signals
CURPWD=`pwd`
DB_FILE=$CURPWD/$1
echo "Testing all signals on $DB_FILE..."
SIGNALS_PATH=$CURPWD/trader/signal
CACHE_PATH=$CURPWD/test_cache

mkdir -p test_cache

for filename in $(find $SIGNALS_PATH -maxdepth 1 -name "*.py")
do
	signal=$(basename $filename | sed 's/.py//')
	if [[ $signal = '__init__' ]]; then
		continue
	elif [[ $signal = 'NULL_Signal' ]]; then
	       	continue
       	fi
	echo "Testing signal $signal..."
	python $CURPWD/tools/binance_simulate.py -f $DB_FILE -g $signal -c test_cache
done

find $CACHE_PATH -name "*.txt" -print -exec cat {} \;
