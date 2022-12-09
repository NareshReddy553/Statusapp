# syntax=docker/dockerfile:1
FROM python:3.7-slim-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /Django
COPY requirements.txt /Django/
RUN pip install -r requirements.txt
COPY . /Django/