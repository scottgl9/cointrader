#!/usr/bin/python

import os.path
import time
import sys
import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect('cryptocurrency_database.ticker_collection_04282018.db')
    c = conn.cursor()

    csv_filename = ''
    if len(sys.argv) == 2:
        csv_filename = sys.argv[1]

    count = 0

    print("Opening {}".format(csv_filename))

    with open(csv_filename) as f:
        for line in f:
            count += 1
            if count == 1: continue
            values = line.strip().split(',')
            sqlstr = "INSERT into ticker (J,K,G,E,F,D,I,M,R,a,b,c,h,l,n,o,p,q,s,v,w,x) VALUES({})".format(str(values)[1:-1])
            #print(sqlstr)
            c.execute(sqlstr)

    conn.commit()
    conn.close()
