FROM python:3.10

WORKDIR /app

# Build-time arguments for non-sensitive data
ARG INSTANCE_FAISS_PATH
ARG INSTANCE_CSV_PATH
ARG DB_FAISS_PATH
ARG DB_CSV_PATH
ARG OBJECT_STORAGE_FAISS_PATH
ARG OBJECT_STORAGE_CSV_PATH

# Runtime environment variables
ENV INSTANCE_FAISS_PATH=$INSTANCE_FAISS_PATH
ENV INSTANCE_CSV_PATH=$INSTANCE_CSV_PATH
ENV DB_FAISS_PATH=$DB_FAISS_PATH
ENV DB_CSV_PATH=$DB_CSV_PATH
ENV OBJECT_STORAGE_FAISS_PATH=$OBJECT_STORAGE_FAISS_PATH
ENV OBJECT_STORAGE_CSV_PATH=$OBJECT_STORAGE_CSV_PATH

# 필요한 패키지들 명시
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# uvicorn으로 앱 실행 (파일명이 main.py이고 FastAPI 객체명이 app이라고 가정)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
