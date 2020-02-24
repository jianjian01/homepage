FROM python:3.7

RUN apt update && apt upgrade -y && apt install -y pipenv

ENV mode production
ENV PYTHONPATH "${PYTHONPATH}:/app"

WORKDIR /app

RUN pip install -U  pip && \
    pipenv install --system --deploy --ignore-pipfile

ADD . .
RUN pipenv sync && \
    pip install Babel
RUN pybabel compile -d /app/translations
RUN pip install -e git+https://github.com/kurtmckee/feedparser.git@6.0.0b1#egg=feedparser --no-cache-dir --src /pypi/src

CMD ["gunicorn", "-w", "4", "-b", "127.0.0.1:5000", "app:app"]