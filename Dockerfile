FROM python:3.9.18-alpine
WORKDIR /usr/src/app

RUN apk add build-base py3-rpigpio

ADD watermeter.py .
ADD requirements.txt .
RUN pip install -r requirements.txt

RUN apk del build-base

CMD ["python", "./watermeter.py"]