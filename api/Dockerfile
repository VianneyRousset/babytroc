FROM python:3-alpine

RUN apk update
RUN apk add uv git bash

# to build in uv sync
RUN apk add gcc python3-dev musl-dev linux-headers

# set the working directory
WORKDIR /usr/src/api

# install dependencies
COPY pyproject.toml uv.lock ./
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
