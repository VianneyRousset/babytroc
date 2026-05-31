FROM python:3-alpine

RUN apk update
RUN apk add uv git bash

# to build in uv sync
RUN apk add gcc python3-dev musl-dev linux-headers

# set the working directory
WORKDIR /usr/src/api

# Expose the port the app runs on
EXPOSE 8080

# copy files
COPY src ./src
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY pyproject.toml uv.lock ./

# install dependencies
RUN uv sync --no-group dev


# Define entrypoint
ENTRYPOINT ["uv", "run", "babycli", "server", "start"]
