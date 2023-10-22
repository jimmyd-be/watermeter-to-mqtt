FROM python:3.9.18-alpine
WORKDIR /usr/src/app

ADD watermeter.py .
ADD requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "./watermeter.py"]