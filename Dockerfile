FROM python:3.11-slim

# As if you were doing "cd .."
WORKDIR /app

COPY . .

# RUN command: like trying to run a linux command
RUN pip install -r requirements.txt

CMD [ "python", "src/app/manage.py", "runserver"]

