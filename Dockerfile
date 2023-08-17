# syntax=docker/dockerfile:1
FROM python:3.9.7
RUN  apt-get update
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /usr/src/tsapp_backend
COPY requirements.txt ./
RUN pip install --upgrade pip --no-cache-dir
RUN pip install -r requirements.txt
COPY . ./
