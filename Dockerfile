FROM python:3.6.5-jessie

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y jq \
        curl

COPY . .

ENTRYPOINT ["/entrypoint.sh"]
