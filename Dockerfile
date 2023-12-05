FROM python:3
COPY main.py req.py . 
COPY ./requirements.txt /TUBES/requirements.txt
WORKDIR /TUBES
RUN pip install --no-cache-dir --upgrade -r /TUBES/requirements.txt
CMD [ "uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]
