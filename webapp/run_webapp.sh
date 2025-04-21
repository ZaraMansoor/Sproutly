#!/bin/bash
cd backend
daphne -e ssl:8443:privateKey=key.pem:certKey=cert.pem webapps.asgi:application > backend.log 2>&1 &

python mqtt_subscriber.py > mqtt.log 2>&1 &

cd ../frontend
http-server ./build -S -C cert.pem -K key.pem -p 3000 > frontend.log 2>&1 &