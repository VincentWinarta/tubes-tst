FROM python:3
ADD main.py .
COPY . /TUBES
WORKDIR /TUBES
RUN pip install fastapi uvicorn geocoder
CMD [ "uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]