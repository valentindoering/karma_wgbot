#!/bin/bash

cd data

if [ ! -f "data_save.json" ]; then
  echo "Error: data_save.json not found in current directory"
  exit 1
fi

rm data.json
mv data_save.json data.json