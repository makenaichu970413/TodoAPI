FROM python:3.9.0

RUN mkdir /code
WORKDIR /code
COPY . .

# COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN python -m spacy download ru_core_news_md

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]


EXPOSE 5000

CMD ["python3", "-u", "-m", "flask", "run", "--host=0.0.0.0"] && ["gunicorn","--bind","0.0.0.0:$PORT","wsgi"]