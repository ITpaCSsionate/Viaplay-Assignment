FROM python:3.8-bullseye

WORKDIR /usr/src/app
COPY Src/ .

RUN apt update 
RUN apt upgrade -y
RUN python3 -m pip install -r requirements.txt

CMD python3 pyApp.py 8080 