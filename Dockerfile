FROM python:3.13.3-slim-bookworm
WORKDIR /usr/src/app

RUN apt install -y build-essential python3-lgpio

ADD watermeter.py .
ADD requirements.txt .
RUN pip install -r requirements.txt

RUN apt purge -y build-essential

CMD ["python", "./watermeter.py"]
