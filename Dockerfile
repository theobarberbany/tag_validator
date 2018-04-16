FROM python:3.6.5-jessie

WORKDIR /usr/src/validator

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["/entrypoint.sh"]
