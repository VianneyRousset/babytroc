FROM python:3-alpine

RUN apk update
RUN apk add uv git bash

# set the working directory
WORKDIR /usr/src/api

# install dependencies
COPY pyproject.toml .
RUN uv sync --no-group dev

# Expose the port the app runs on
EXPOSE 8080

COPY app ./app
COPY entrypoint.sh .
COPY alembic.ini .
COPY alembic ./alembic

# Define entrypoint
# docker will run the following script when started
ENTRYPOINT ["./entrypoint.sh"]
