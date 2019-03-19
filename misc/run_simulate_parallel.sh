#!/bin/bash
signal_name="Hybrid_Crossover_Test"
if [ "$#" -eq 1 ]; then
	signal_name=$1
fi

echo "Using signal $signal_name"

DB_LIST="cryptocurrency_database.miniticker_collection_04032018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_04092018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_05312018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_11202018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_11232018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_01192019.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_01202019.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_03142019.db"
echo $DB_LIST | tr ' ' '\n' | parallel -j 4 python tools/binance_simulate.py -f {} -g $signal_name
