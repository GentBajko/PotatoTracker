start:
	dotnet watch run

build:
	docker build -t potato-tracker .

up:
	docker-compose up -d

mongo:
	docker-compose up -d mongo

down:
	docker-compose down

clear:
	docker-compose down -v

run:
	docker run --rm --name potato-tracker potato-tracker
