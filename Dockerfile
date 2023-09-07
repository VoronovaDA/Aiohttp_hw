FROM python:3.11

WORKDIR /Aiohttp_hw

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .