# Development
create_venv:
	python -m venv venv
	source ./venv/bin/activate
	poetry install

# Deployment
build:
	poetry build 

build_image:
	docker build . -t inference-engine:latest

publish:
	docker tag inference-engine:latest tiencheng/inference-engine:latest
	docker push tiencheng/inference-engine:latest

# Documentation
clean_docs:
	rm docs/source/api -rf
	rm docs/build

make_docs:
	source ./venv/bin/activate
	cd docs
	make html

update_docs:
	clean_docs make_docs
