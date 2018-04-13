FROM python:3

WORKDIR /usr/src/validator

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
