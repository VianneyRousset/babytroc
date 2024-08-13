#!/usr/bin/env sh

# start the server
uvicorn app.main:app --host "0.0.0.0" --port 8080 --reload
