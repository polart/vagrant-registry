#!/usr/bin/env bash


DB_NAME='vagrant_registry'
DB_USER='vagrant_registry'
DB_PASSWORD='vagrant_registry'

create_db="psql -c $'SELECT 1 FROM pg_database WHERE datname=\'$DB_NAME\';' | "
create_db+="grep -q 1 || "
create_db+="createdb $DB_NAME"
su postgres -c "$create_db" || true

create_user="psql $DB_NAME -c $'SELECT 1 FROM pg_roles WHERE rolname=\'$DB_USER\';' | "
create_user+="grep -q 1 || "
create_user+="(psql $DB_NAME -c $'create user $DB_USER with password \'$DB_PASSWORD\';' && "
create_user+="psql $DB_NAME -c 'grant all privileges on database $DB_NAME to $DB_USER;' && "
create_user+="psql $DB_NAME -c 'alter schema public owner to $DB_USER;')"
su postgres -c "$create_user" || true

python3 manage.py migrate
python3 manage.py collectstatic --no-input
