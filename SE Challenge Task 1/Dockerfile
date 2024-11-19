

FROM python:3.9

WORKDIR /workspace 

COPY . /workspace

RUN pip install requests

ENV API_URL="https://u8whitimu7.execute-api.ap-southeast-1.amazonaws.com/prod"

ENTRYPOINT ["python", "main.py"]