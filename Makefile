.PHONY: help

all: help

help:
	@echo "available targets:"
	@echo "run         :    run tweetcards in pipenv"

run:
	pipenv run flask run


