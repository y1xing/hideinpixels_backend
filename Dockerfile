FROM python:3.11
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN apt update
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./app /code/app
WORKDIR /code/app
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
EXPOSE 80
