#!/bin/bash

pip install .

if `echo "select * from bots;" | psql $DATABASE_URL`; then
  echo "Config Found, booting"
  grace start
else
  echo "Config not found, seeding new one"
  grace db create
  grace db seed
  grace start
fi
