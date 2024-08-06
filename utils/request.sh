#!/usr/bin/env bash

set -eu

TOKEN_FILE="$(dirname $0)/.token"
URL='localhost:8000/api'

# get method
method=${0##*/}
method=${method%.sh}
if [ "$method" = 'request' ]; then
	method="$1"
	shift
fi
method="${method^^}"

# read token
token="$(cat $TOKEN_FILE)"

# get endpoint
endpoint="$1"
shift

# format arg with --data 'arg'
declare -a data_args=()
for arg in "$@"; do
	data_args+=("--data '$arg'")
done

eval set -- "${data_args[@]}"

curl --request "${method}" --cookie "token=${token}" "$URL/$endpoint" "${@}" | jq
