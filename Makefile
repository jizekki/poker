manage:
	@poetry run python3 manage.py $(filter-out $@, $(MAKECMDGOALS))

pytest:
	@poetry run pytest --cov --cov-report html --cov-report term -vv

source:
	echo "type : ```deactivate``` to exit the shell"
	@poetry shell

compose:
	@docker-compose build && docker-compose up -d

stop:
	@docker-compose down
