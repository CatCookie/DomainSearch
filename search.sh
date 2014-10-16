#!/bin/sh

echo "Searching for $1 \n"
cd src/main
python3 DomainSearch.py -qq $1
python3 DomainSearchDB.py $1
cd ../../
