#!/bin/bash

cd data
if [ -f "data_save.json" ]; then
  echo "Error: data_save.json not found in current directory"
  exit 1
fi
mv data.json data_save.json
cp backup_data.json data.json