FROM python:3.7-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers

WORKDIR /heehawbot

COPY config.json ./config.json
COPY requirements.txt ./requirements.txt
COPY ./bot ./bot

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "bot"]