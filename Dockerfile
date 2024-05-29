FROM python:3.12.3-alpine

WORKDIR /app

# Based on: https://stackoverflow.com/a/68190141/10763533
RUN apk add --no-cache gcc musl-dev mariadb-connector-c-dev

COPY requirements.txt .

RUN pip install mysqlclient
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]

