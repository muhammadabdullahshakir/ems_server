# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.9

# Install manually all the missing libraries
RUN apt-get update
RUN apt-get install -y gconf-service


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
ENV PORT 8080

WORKDIR $APP_HOME
COPY . .

CMD exec gunicorn --bind :$PORT --threads 3 ems_project.wsgi