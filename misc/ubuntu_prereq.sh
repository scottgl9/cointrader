#!/bin/sh
apt-get update
apt-get install -y python3-pip python3-autobahn python3-flask python3-twisted python3-tz python3-numpy python3-six 
apt-get install -y python3-requests python3-matplotlib python3-scipy python3-sklearn python3-pymongo python3-aniso8601
apt-get install -y python3-websocket cython python3-pandas python3-psycopg2 python3-cryptography python3-gevent python3-crontab python3-dateparser
pip3 install --upgrade pip
pip3 install -r requirements.txt
