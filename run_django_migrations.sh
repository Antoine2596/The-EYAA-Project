#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <Répertoire/des/donnees> <mode>"
    exit 1
fi

DATA_DIR=$1
MODE=$2

python manage.py makemigrations
python manage.py makemigrations core
python manage.py migrate
python manage.py import_my_data "$DATA_DIR" "$MODE"
