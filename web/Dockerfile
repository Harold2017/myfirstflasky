FROM python:3.5

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ONBUILD COPY requirements.txt /usr/src/app/
PNBUILD RUN pip install --no-cache-dir -r requirements.txt

ONBUILD COPY . /usr/src/app