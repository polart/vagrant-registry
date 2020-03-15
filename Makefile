.PHONY: help
.DEFAULT_GOAL := help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build:
	docker-compose build

build-client:
	docker-compose run client yarn build

build-prod:
	build-client
	docker build -t polart/vagrant-registry:0.1.0 .

install_client:
	docker-compose run client yarn --frozen-lockfile

migrate:
	docker-compose run api python manage.py migrate

create_superuser:
	docker-compose run api python manage.py createsuperuser

start:
	docker-compose up

stop:
	docker-compose down

test:
	docker-compose run api python manage.py test
