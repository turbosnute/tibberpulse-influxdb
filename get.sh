#!/bin/bash

while :
do
  date
  echo "--- Starting Python script..."
  /bin/python3 -u pulse.py
  echo "---"
  date
  echo "Sleep 60"
  sleep 60
done
