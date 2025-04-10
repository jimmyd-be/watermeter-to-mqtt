FROM ubuntu:rolling
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y build-essential python3-pip

ADD watermeter.py .
ADD requirements.txt .
RUN pip3 install -r requirements.txt

RUN apt-get purge -y build-essential

CMD ["python", "./watermeter.py"]
