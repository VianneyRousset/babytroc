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
# API_APP [default: "app.main:app"]
#   APP to run.
#
# TEST_MODE [default: "false"]
#   Run test and exit

set -eu

: ${API_HOST:="0.0.0.0"}
: ${API_PORT:=8080}
: ${API_APP:="app.main:app"}
: ${API_PREFIX:=".main:app"}

: ${API_TEST_MODE:=false}

# test mode
if ${API_TEST_MODE}; then
  pytest --color=yes -n 8 -vv

# production mode
else
  gunicorn \
    --workers=1 \
    --bind="${API_HOST}:${API_PORT}" \
    ${API_APP}

fi
