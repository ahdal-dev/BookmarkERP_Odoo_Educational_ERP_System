#!/bin/bash
# Starts Odoo against the Railway Postgres. On first start (empty database) it
# initialises the DB and installs every custom addon, then sets the admin
# user's password from ODOO_PASSWORD.
set -e
: "${PGHOST:?}" "${PGUSER:?}" "${PGPASSWORD:?}" "${ODOO_PASSWORD:?}"
DB="${ODOO_DB:-edu_demo_new}"
export PGPORT="${PGPORT:-5432}"
ADDONS=/mnt/extra-addons/edu_mangment,/mnt/extra-addons/open_edu_cat
BASE=(odoo --db_host="$PGHOST" --db_port="$PGPORT" --db_user="$PGUSER" --db_password="$PGPASSWORD" \
      --db-filter="^${DB}\$" --addons-path="/usr/lib/python3/dist-packages/odoo/addons,$ADDONS" \
      --http-port=8081 --proxy-mode --workers=0 --without-demo=all)

export PGDATABASE=postgres
if ! psql -tAc "select 1 from pg_database where datname='$DB'" | grep -q 1 \
   || ! PGDATABASE="$DB" psql -tAc "select 1 from ir_module_module limit 1" >/dev/null 2>&1; then
  echo "Initialising database $DB"
  MODS=$(for d in /mnt/extra-addons/*/*/; do [ -f "$d/__manifest__.py" ] && basename "$d"; done | paste -sd,)
  "${BASE[@]}" -d "$DB" -i "base,$MODS" --stop-after-init
  echo "env['res.users'].search([('login','=','${ODOO_USERNAME:-admin}')]).write({'password': '$ODOO_PASSWORD'}); env.cr.commit()" \
    | "${BASE[@]}" -d "$DB" shell
fi
exec "${BASE[@]}" -d "$DB"
