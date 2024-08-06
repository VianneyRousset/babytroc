#!/usr/bin/env sh

NAME="kindbaby-gui"
ID=$(docker ps | grep ${NAME} | cut --delimiter " " --fields 1)

docker exec -it "$ID" sh
