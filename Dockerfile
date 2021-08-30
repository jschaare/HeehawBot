FROM python:3.8.5-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers libffi-dev

WORKDIR /heehawbot

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY config.json ./config.json
COPY ./heehawbot ./heehawbot

CMD ["python", "-m", "heehawbot"]