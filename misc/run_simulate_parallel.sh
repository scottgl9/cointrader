#!/bin/bash
DB_LIST="cryptocurrency_database.miniticker_collection_04032018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_04092018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_05312018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_11202018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_11232018.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_01192019.db"
DB_LIST+=" cryptocurrency_database.miniticker_collection_01202019.db"
echo $DB_LIST | tr ' ' '\n' | parallel -j 2 python tools/binance_simulate.py -f {}
