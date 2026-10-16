FROM python:3.9

RUN apt update && apt upgrade -y && pip install -U "poetry<2" -i https://mirrors.bfsu.edu.cn/pypi/web/simple

ENV mode production
ENV PYTHONPATH "${PYTHONPATH}:/app"
RUN mkdir -p /static/site/
WORKDIR /app

COPY poetry.lock ./
COPY pyproject.toml ./

RUN poetry config virtualenvs.create false  && poetry install --no-dev --no-interaction
RUN pip install -U cchardet -i https://mirrors.bfsu.edu.cn/pypi/web/simple
ADD . .

RUN pybabel compile -d /app/translations

CMD ["gunicorn", "-w", "1", "-b", "127.0.0.1:5000", "app:app"]
