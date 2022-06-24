FROM python:3.9.12-buster

WORKDIR /app

EXPOSE 5050

COPY . /app/

RUN pip install poetry && poetry install --no-root --no-dev;

CMD ["poetry", "run", "flask", "run"]
