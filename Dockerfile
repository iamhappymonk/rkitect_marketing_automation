FROM python:3.12-slim

WORKDIR /app

COPY drip_mail/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY drip_mail/ ./drip_mail/

CMD ["sh", "-c", "uvicorn drip_mail.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
