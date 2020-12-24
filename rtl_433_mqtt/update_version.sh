#!/bin/bash

sed -i -E -e "s/(version\":.).*/\1\"$(date +%s)\",/" config.json
