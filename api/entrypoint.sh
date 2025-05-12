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

set -eu

: ${API_HOST:="0.0.0.0"}
: ${API_PORT:=8080}
: ${API_APP:="app.main:app"}
: ${API_PREFIX:=""}

uvicorn ${API_APP} \
  --host=${API_HOST} \
  --port=${API_PORT} \
  --root-path ${API_PREFIX}
