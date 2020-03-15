FROM python:3.8.2-alpine3.11


RUN set -ex && \
    apk update && \
    apk add --no-cache --virtual .build-dependencies gcc=~9 musl-dev postgresql-dev

COPY requirements/* /project/requirements/

RUN pip install --no-cache-dir -r /project/requirements/dev.txt

EXPOSE 8000

WORKDIR /project

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
