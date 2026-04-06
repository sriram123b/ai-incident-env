FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn pydantic

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]