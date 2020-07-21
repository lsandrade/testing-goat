FROM python:3.7
RUN mkdir /superlists
WORKDIR /superlists
COPY requirements.txt /superlists/
RUN pip install -r requirements.txt
COPY /superlists/ /superlists/

EXPOSE 8000