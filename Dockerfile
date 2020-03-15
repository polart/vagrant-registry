FROM ubuntu:16.04

LABEL maintainer="Artem Polunin"

ENV DJANGO_SETTINGS_MODULE vagrant_registry.settings.production
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get clean && apt-get update && apt-get install -y locales && \
    locale-gen en_US.UTF-8 && \
    apt-get install -y \
    python3.5 python3-pip \
    postgresql-9.5 libpq-dev \
    nginx \
    supervisor

WORKDIR /code
# Run it before adding /code dir in order to cache pip installs
ADD ./api/requirements /code/api/requirements
RUN pip3 install -r api/requirements/production.txt

ADD . /code

RUN mkdir -p /logs/nginx /logs/supervisord /logs/gunicorn /logs/django

RUN cp conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

# Correct the PG error: could not open temporary statistics file "/var/run/postgresql/9.5-main.pg_stat_tmp/global.tmp": No such file or directory
RUN mkdir -p /var/run/postgresql/9.5-main.pg_stat_tmp
RUN chown postgres.postgres /var/run/postgresql/9.5-main.pg_stat_tmp -R

# Configure Nginx
RUN ln -s /code/conf/nginx.conf /etc/nginx/sites-enabled/vagrant_registry
RUN rm /etc/nginx/sites-enabled/default


CMD ["/usr/bin/supervisord"]
