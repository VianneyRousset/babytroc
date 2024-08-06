#!/usr/bin/env bash

set -eu

URL=login
EMAIL="${DEV_USER_EMAIL}"
PASSWORD="${DEV_USER_PASSWORD}"
TOKEN_FILENAME=.token

(
	token=$(
		set -e
		set -o pipefail
		curl -X POST --fail "localhost:8000/api/$URL" --data "email=$EMAIL" --data "password=$PASSWORD" |
			jq --raw-output '.token'
	) || exit 1
	echo "$token" >$TOKEN_FILENAME
	echo "Token file '$TOKEN_FILENAME' updated" >&1
) || echo "Failed to updated token" >&1
