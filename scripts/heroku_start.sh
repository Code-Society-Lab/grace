#!/bin/bash

if psql $DATABASE_URL "SELECT * FROM bots;"; then
  echo "Config Found, booting"
  grace start
else
  echo "Config not found, seeding new one"
  grace db create
  grace db seed
  grace start
fi
