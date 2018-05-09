FROM    tiangolo/uwsgi-nginx-flask:python3.6

MAINTAINER Troy Caro "troy.caro@pitt.edu"

ENV		TZ=America/New_York

RUN		pip install requests redis

ADD     /building_flask /app
