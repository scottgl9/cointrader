#!/bin/bash
#signal_name="Hybrid_Crossover_Test"
#strategy_name="basic_signal_market_strategy"
#if [ "$#" -eq 1 ]; then
#	signal_name=$1
#elif [ "$#" -eq 2 ]; then
#	signal_name=$1
#	strategy_name=$2
#fi

#echo "Using signal $signal_name"

#DB_LIST="cryptocurrency_database.miniticker_collection_04032018.db"
#DB_LIST+=" cryptocurrency_database.miniticker_collection_04092018.db"
#DB_LIST+=" cryptocurrency_database.miniticker_collection_05312018.db"
#DB_LIST+=" cryptocurrency_database.miniticker_collection_11202018.db"
#DB_LIST+=" cryptocurrency_database.miniticker_collection_11232018.db"
#DB_LIST+=" cryptocurrency_database.miniticker_collection_01192019.db"
#DB_LIST+=" cryptocurrency_database.miniticker_collection_01202019.db"
#DB_LIST+=" cryptocurrency_database.miniticker_collection_03142019.db"
#DB_LIST+=" cryptocurrency_database.miniticker_collection_06182019.db"
DB_LIST="`find . -name \"cryptocurrency_*.db\" | tr '\n' ' '`"
echo $DB_LIST | tr ' ' '\n' | parallel -j 3 python tools/binance_simulate.py -f {}
