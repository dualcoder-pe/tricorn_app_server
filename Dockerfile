FROM python:3.11.10

COPY Pipfile ./
COPY Pipfile.lock ./

RUN python3 -m pip install --upgrade pip
RUN pip3 install pipenv && pipenv requirements > requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app
WORKDIR /app
