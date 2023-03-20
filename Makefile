build:
	docker build -t potato-tracker .

run:
	docker run --rm --name potato-tracker potato-tracker
