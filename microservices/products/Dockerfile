FROM python:3.11-slim

# As if you were doing "cd .."
WORKDIR /app

COPY . .

# RUN command: like trying to run a linux command
RUN pip install -r requirements.txt

EXPOSE 8001

CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

