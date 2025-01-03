#!/bin/bash -eu
set -o pipefail

readonly COMPOSE_FILE=compose-test.yaml

export POSTGRES_USER=test
export POSTGRES_PASSWORD=test

docker_compose() {
	docker compose -f "$COMPOSE_FILE" "$@"
}

with_compose() {
	docker_compose up --detach --build --renew-anon-volumes
	cleanup() {
		docker_compose down
	}
	trap cleanup EXIT

	export POSTGRES_HOST=localhost
	export POSTGRES_PORT=$(docker_compose port db 5432 | cut -d: -f2)
	export IMGPUSH_HOST=localhost
	export IMGPUSH_PORT=$(docker_compose port images 5000 | cut -d: -f2)

	COUNTER=60 # 1 min timeout
	while ! docker_compose logs db 2>/dev/null |
		grep --quiet 'database system is ready to accept connections' ||
		! curl --silent localhost:${IMGPUSH_PORT}
	do
		COUNTER=$((COUNTER - 1))
		[ $COUNTER -eq 0 ] && break
		sleep 1
	done

	"$@"
}

with_compose pytest "$@"
