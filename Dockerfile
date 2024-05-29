FROM python:3.12.3-alpine

WORKDIR /app

# Based on: https://stackoverflow.com/a/68190141/10763533
RUN apk add --no-cache gcc musl-dev mariadb-connector-c-dev

COPY ./pyproject.toml ./README.md ./backend /app/
COPY ./backend /app/backend/

RUN pip install .

COPY . .

CMD ["python", "backend/app.py"]

