#!/bin/bash
for file in `find . -name "cryptocurrency_*.db"`
do
	python tools/binance_simulate.py -f $file
done
