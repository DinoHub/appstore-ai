POETRY ?= $(FLAGS) poetry
init_repo:
	@echo "Getting latest version of repository"
	git fetch && git pull
	@echo "Setting default commit template"
	git config --local commit.template ../.github/ct.md

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
install_precommit:
	@echo "Installing precommit hook"
	source ./venv/bin/activate
	cd .. & pre-commit install

setup: create_venv install 

init_server: 
	. venv/bin/activate && mlaunch init --single --port 4051 --name "app_store";\

start_server: 
	@echo "Starting MongoDB"
	-@if [ -d "data" ];then\
		. venv/bin/activate && mlaunch start;\
	else\
		echo "No mlaunch data, run make init_server";\
	fi

stop_server:
	@echo "Stopping MongoDB"
	@if [ -d "data" ];then\
		. venv/bin/activate && mlaunch stop;\
	else\
		echo "No mlaunch data, run make init_server";\
	fi

.PHONY: fix-poetry-conflicts
fix-poetry-conflicts: ## Attempts to fix Poetry merge/rebase conflicts by choosing theirs and locking again
	git checkout --theirs poetry.lock
	$(MAKE) poetry-relock

.PHONY: fix-poetry-conflicts-2
fix-poetry-conflicts-2: ## Another way to try to fix Poetry merge/rebase conflicts
	git restore --staged --worktree poetry.lock
	$(MAKE) poetry-relock

.PHONY: poetry-relock
poetry-relock: pyproject.toml ## Run poetry lock w/o updating deps, use after changing pyproject.toml trivially
	$(POETRY) lock --no-update
