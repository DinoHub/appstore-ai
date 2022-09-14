init_repo:
	@echo "Getting latest version of repository"
	git fetch && git pull
	@echo "Setting default commit template"
	git config --local commit.template .github/ct.md

create_venv:
	@echo "Setting up virtual environment"
	python -m venv venv
	source ./venv/bin/activate
	@echo "Installing poetry"
	pip install poetry

install: poetry.lock
	@echo "Installing dependencies"
	source ./venv/bin/activate
	poetry install

setup: create_venv install