FROM ubuntu:rolling
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y build-essential

ADD watermeter.py .
ADD requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get purge -y build-essential

CMD ["python", "./watermeter.py"]
