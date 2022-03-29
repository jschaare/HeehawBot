FROM python:3.8.5-slim

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install git libffi-dev ffmpeg

WORKDIR /heehawbot

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY config.json ./config.json
COPY ./heehawbot ./heehawbot

CMD ["python", "-m", "heehawbot"]