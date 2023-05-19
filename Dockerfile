FROM python:3.11-slim-bullseye AS builder

RUN python3 -m venv /venv
ENV PATH=/venv/bin:$PATH

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

FROM python:3.11-slim-bullseye

COPY --from=builder /venv /venv
ENV PATH=/venv/bin:$PATH

WORKDIR /app
COPY . .

# ENTRYPOINT ["python", "app.py"]
CMD ["uvicorn", "app:api", "--port", "80"]