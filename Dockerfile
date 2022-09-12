FROM python:3.8

MAINTAINER ihor

ADD requirements.txt  ./

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

ADD main.py model.py techtask.json /tech_task/

WORKDIR /tech_task/








