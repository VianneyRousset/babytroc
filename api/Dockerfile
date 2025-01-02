FROM python:3.13

# set the working directory
WORKDIR /usr/src/api

# install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expose the port the app runs on
EXPOSE 8080

COPY app ./app
COPY pyproject.toml .
COPY entrypoint.sh .

# Define entrypoint
# docker will run the following script when started
ENTRYPOINT ["./entrypoint.sh"]
