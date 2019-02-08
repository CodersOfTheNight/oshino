__PHONY__: all

pull-containers:
	docker-compose pull

rebuild-compose:
	docker-compose down && docker-compose build

run-integration-tests: pull-containers rebuild-compose
	docker-compose up --remove-orphans --abort-on-container-exit --exit-code-from oshino-query

run-dev-environment: pull-containers rebuild-compose
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --remove-orphans
