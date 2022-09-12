FROM python:3

MAINTAINER ihor

WORKDIR /tech_task

ADD requirements.txt  ./

RUN pip install --no-cache-dir -r requirements.txt

ADD main.py model.py ./







