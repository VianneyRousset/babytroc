#!/usr/bin/env bash
#
# Start the API app
#
# ENVIRONMENT
#
# API_HOST [default: 0.0.0.0]
#   Bind socket to this host.
#
# API_PORT [default: 8080]
#   Bind socket to this port.
#
# API_APP [default: "babytroc.main:application"]
#   APP to run.

set -eu

source .venv/bin/activate

: ${API_HOST:="0.0.0.0"}
: ${API_PORT:=8080}
: ${API_APP:="babytroc.main:application"}
: ${API_PREFIX:=""}

alembic upgrade head

uvicorn "${API_APP}" \
  --host="${API_HOST}" \
  --port="${API_PORT}" \
  --root-path="${API_PREFIX}"
