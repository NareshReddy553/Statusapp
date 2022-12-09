
# FROM python:3.7
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED=1
# WORKDIR /Django
# COPY . /Django/
# RUN pip install --upgrade pip --no-cache-dir
# RUN pip install -r requirements.txt
# CMD ["python3","manage.py","runserver",]


# syntax=docker/dockerfile:1
FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# ENV MYSQL_ROOT_PASSWORD 16e91a0553
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip --no-cache-dir
RUN pip install -r requirements.txt
COPY . /code/
# CMD ["python","manage.py","runserver"]

