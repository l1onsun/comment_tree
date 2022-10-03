-include .env
export

test-docker:
	docker compose -f docker-compose.yml build
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm app

test-unit:
	pytest -m unit

test-all:
	pytest

check:
	pre-commit run -a

install:
	pip install -r requirements.txt
	pre-commit install

requirements.txt: requirements.in
	CUSTOM_COMPILE_COMMAND="make requirements.txt" pip-compile \
		--output-file=requirements.txt \
		--generate-hashes \
		--verbose \
		requirements.in

sync:
	pip-sync requirements.txt


run:
	uvicorn --factory comments_tree.asgi:app_factory

run-docker:
	docker compose -f docker-compose.yml up

stop-test-postgres:
	docker compose stop postgres_test

alembic-autogenerate-revision:
	docker compose -f docker-compose.yml build
	docker compose -f docker-compose.yml -f docker-compose.migration.yml run --rm app


