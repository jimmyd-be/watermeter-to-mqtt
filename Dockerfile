FROM ubuntu:latest
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    build-essential \
    swig \
    python3-dev \
    python3-setuptools \
    liblgpio-dev \
    python3-pip

ADD watermeter.py .
ADD requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

RUN apt-get purge -y build-essential \
    swig \
    python3-dev \
    python3-setuptools \
    liblgpio-dev

CMD ["python3", "./watermeter.py"]
