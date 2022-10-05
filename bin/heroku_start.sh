#!/bin/bash

generate_config() {
  config_path=/app/config/database.cfg

  if [ ! -f $config_path ]; then
    cat /app/bin/templates/heroku.database.template.cfg > $config_path
  fi
}

init() {
  table_count=$(psql -qAt "$DATABASE_URL" -c "select count(*) from information_schema.tables where table_schema = 'public';")

  if [ $table_count -eq "0" ]; then
    echo "Configuring the database"

    grace db create
    grace db seed
  fi
}

generate_config

pip install .
init
grace start
