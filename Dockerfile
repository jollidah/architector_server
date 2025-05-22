FROM python:3.10

WORKDIR /app

# 필요한 패키지들 명시
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# uvicorn으로 앱 실행 (파일명이 main.py이고 FastAPI 객체명이 app이라고 가정)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
