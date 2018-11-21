__PHONY__: all

pull-containers:
	docker-compose pull

rebuild-compose:
	docker-compose down && docker-compose build

run-integration-tests: pull-containers rebuild-compose
	docker-compose up --remove-orphans
