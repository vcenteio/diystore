FROM python:3.10-buster

WORKDIR /app

EXPOSE 5050

COPY . /app/

RUN pip install poetry && poetry install --no-root --no-dev;

CMD ["poetry", "run", "flask", "run"]
