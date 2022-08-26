FROM python:3.10-buster

WORKDIR /app

EXPOSE 5050

COPY . /app/

RUN /bin/bash -c "pip install poetry && poetry export > requirements.txt && pip install -r requirements.txt;"

CMD gunicorn $API_APP