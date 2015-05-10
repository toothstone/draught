#!/bin/sh
cd /home/draught/draught

exec /usr/local/bin/uwsgi \
    --master \
    --socket 0.0.0.0:5000 \
    --wsgi-file draught.py \
    --callable app
