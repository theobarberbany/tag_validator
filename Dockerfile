FROM python:3.6.5-jessie

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y jq \
        curl

COPY . ./
RUN echo '#!/bin/bash' > /usr/bin/validator
RUN echo 'python /validator.py "$@"' >> /usr/bin/validator && \
    chmod +x /usr/bin/validator

ENTRYPOINT ["/entrypoint.sh"]
