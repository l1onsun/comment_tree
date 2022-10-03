Тестовое задание (ТЗ: [terms_of_reference](terms_of_reference.md))

## Using with docker
### Run all tests in docker-compose
```shell
> make test-docker stop-test-postgres
```
### Deploy in docker-compose
```shell
> make run-docker
```

## Using locally
### Install dependencies
```shell
> # activate venv
> make install
```
### Run only unit tests
```shell
> make test-unit
```
### Run all tests
```shell
> # set TEST_POSTGRES_URI in .env
> make test-all
```
### Change dependencies
```shell
> # edit requirements.in
> make requirements.txt sync
```
