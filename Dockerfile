FROM python:3.7

RUN apt update && apt upgrade -y && apt install -y pipenv

ENV mode production

WORKDIR /app
ADD . .

RUN pip install -U  pip && pipenv install --system --deploy --ignore-pipfile && pipenv sync
RUN export PYTHONPATH="${PYTHONPATH}:/app"

CMD ["gunicorn", "-w", "4", "-b", "127.0.0.1:5000", "app:app"]