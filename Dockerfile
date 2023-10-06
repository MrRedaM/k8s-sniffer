FROM python:3.8-slim-buster

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y tcpdump

RUN pip install -r requirements.txt

CMD ["python", "main.py"]