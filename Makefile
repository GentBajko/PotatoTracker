build:
	docker build -t potato-tracker .

up:
	docker-compose up -d

down:
	docker-compose down

clear:
	docker-compose down -v

run:
	docker run --rm --name potato-tracker potato-tracker
