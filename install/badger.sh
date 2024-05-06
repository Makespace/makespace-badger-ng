#!/bin/sh

DIR=${HOME}/makespace-badger-ng

cd ${DIR}

python3 ./main.py ui --port=/dev/ttyUSB0 -d ./badge.db --printer=vretti --sound
