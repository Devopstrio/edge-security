FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install .

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY src/ src/

ENV PYTHONPATH=/app/src
EXPOSE 8001
CMD ["python", "src/edgesecurity/main.py"]
