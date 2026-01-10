include .env

.PHONY: db-up db-down db-remove

db-create:
	docker run --name $(POSTGRES_CONTAINER_NAME) -e POSTGRES_DB=$(POSTGRES_DB) -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -p $(POSTGRES_PORT):5432 -d postgres:15

db-run:
	docker start ${POSTGRES_CONTAINER_NAME}

db-down:
	docker stop $(POSTGRES_CONTAINER_NAME)

db-remove:
	docker rm $(POSTGRES_CONTAINER_NAME)

test-mail:
	docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

