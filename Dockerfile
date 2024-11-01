FROM python:3.12-slim
WORKDIR /app

COPY . /app

RUN pip install --no-cache uv && uv pip install --system --no-cache -r requirements.txt

EXPOSE 8009

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8009"]