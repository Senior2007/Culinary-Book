FROM python:3.12-slim

WORKDIR /app

COPY Backend/requirements.txt Backend/requirements.txt
RUN pip install --no-cache-dir -r Backend/requirements.txt

COPY Backend/ Backend/
COPY Frontend/ Frontend/

ENV PYTHONPATH=/app/Backend/library/src
ENV PORT=8000
EXPOSE 8000

WORKDIR /app/Backend

CMD ["sh", "-c", "uvicorn endpoints:app --host 0.0.0.0 --port ${PORT:-8000}"]
