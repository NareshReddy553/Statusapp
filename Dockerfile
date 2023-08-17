
# FROM python:3.9.7
# RUN apt-get update && apt-get install gcc libaio1 wget unzip -y
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
# WORKDIR /usr/src/tsapp_backend
# COPY requirements.txt ./
# RUN pip install --upgrade pip --no-cache-dir
# RUN pip install -r requirements.txt
# COPY . ./

# syntax=docker/dockerfile:1
FROM python:3.9.7
RUN apt-get update
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip --no-cache-dir
RUN pip install -r requirements.txt
COPY . /code/