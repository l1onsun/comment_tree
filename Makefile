-include .env
export

requirements.txt: requirements.in
	CUSTOM_COMPILE_COMMAND="make requirements.txt" pip-compile \
		--output-file=requirements.txt \
		--generate-hashes \
		--verbose \
		requirements.in

install:
	pip install -r requirements.txt
	pre-commit install

sync:
	pip-sync requirements.txt

check:
	pre-commit run -a

test-unit:
	pytest -m unit

test-all:
	pytest

docker-test: docker-build
	DOCKER_COMMAND="pytest" \
		make docker-custom-command

run:
	uvicorn --factory comments_tree.asgi:create_app

docker-build:
	docker compose -f docker-compose.yml build

docker-run: docker-build
	docker compose -f docker-compose.yml up

docker-custom-command: docker-build
	docker compose \
		-f docker-compose.yml -f docker-compose.custom-command.yml \
		run --rm app

docker-stop-postgres:
	docker compose stop postgres_test

alembic-upgrade-head:
	DOCKER_COMMAND="alembic upgrade head" \
		make docker-custom-command

alembic-stamp-head:
	DOCKER_COMMAND="alembic stamp head" \
		make docker-custom-command

alembic-autogenerate:
ifndef REVISION_NAME
	$(error REVISION_NAME is undefined)
endif
	DOCKER_COMMAND="alembic revision --autogenerate -m '${REVISION_NAME}'" \
 		make docker-custom-command