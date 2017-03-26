#!/usr/bin/env bash

# Test overflow above 999
for i in {1..1000}
do
    python2 client.py inc 2> /dev/null
done

read -n1 -r -p "Press any key to continue..." key

# Test overflow below 0
python2 client.py dec 2> /dev/null
python2 client.py inc 2> /dev/null

read -n1 -r -p "Press any key to continue..." key

# Random inc and dec
for i in {1..100}
do
  if [ $(( $RANDOM % 2 )) -eq 0 ]; then
    python2 client.py inc 2> /dev/null
  else
    python2 client.py dec 2> /dev/null
  fi
done
