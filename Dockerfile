FROM python:3.12


LABEL authors="Aziz Ben Anaya email: benanayaka@gmail.com"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

CMD ["python", "app.py"]
