# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.8.10

WORKDIR /my_civil_service_project
# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Mounts the application code to the image
COPY . my_civil_service_project

COPY /entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

