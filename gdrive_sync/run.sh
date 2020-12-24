#!/usr/bin/env bashio

folder="$(bashio::config 'folder')"

project_id="$(bashio::config 'project_id')"
client_id="$(bashio::config 'client_id')"
client_secret="$(bashio::config 'client_secret')"

cp credentials.json.tmpl /data/credentials.json
sed -i \
    -e s/PROJECT_ID/$project_id/ \
    -e s/CLIENT_ID/$client_id/ \
    -e s/CLIENT_SECRET/$client_secret/ \
    /data/credentials.json

go run github.com/dknowles2/gdrive_sync \
   --input_dir=/share/scans \
   --output_dir="Incoming Scans" \
   --creds_file=/data/credentials.json \
   --token_file=/data/token.json
