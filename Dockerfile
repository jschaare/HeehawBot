FROM python:3.7-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers

WORKDIR /heehawbot

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY config.json ./config.json
COPY ./bot ./bot

CMD ["python", "-m", "bot"]