#!/bin/sh
apt-get update
apt-get install -y python-pip python-autobahn python-flask python-twisted python-tz python-numpy python-six 
apt-get install -y python-requests python-matplotlib python-scipy python-sklearn python-pymongo python-aniso8601
apt-get install -y python-websocket cython python-pandas python-psycopg2 python-cryptography python-gevent python-crontab
pip install --upgrade pip
pip install dateparser
pip install -r requirements.txt
