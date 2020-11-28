FROM python:3.7

RUN apt update && apt upgrade -y && apt install -y pipenv

ENV mode production
ENV PYTHONPATH "${PYTHONPATH}:/app"
RUN mkdir -p /static/site/
WORKDIR /app

COPY Pipfile* ./

RUN pip install -U  pip && \
    pipenv install --system --deploy --ignore-pipfile
RUN pip install Babel && \
    pip install -e git+https://github.com/kurtmckee/feedparser.git@6.0.0b1#egg=feedparser --no-cache-dir --src /pypi/src


ADD . .

RUN pybabel compile -d /app/translations

CMD ["gunicorn", "-w", "1", "-b", "127.0.0.1:5000", "app:app"]
