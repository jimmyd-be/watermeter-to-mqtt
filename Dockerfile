FROM python:3.13.3-slim-bookworm
WORKDIR /usr/src/app

RUN apt install -y build-base python3-lgpio

ADD watermeter.py .
ADD requirements.txt .
RUN pip install -r requirements.txt

RUN apt purge -y  build-base

CMD ["python", "./watermeter.py"]
