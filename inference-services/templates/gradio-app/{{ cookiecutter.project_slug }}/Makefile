build:
	docker build . -t {{ cookiecutter.project_slug }}:{{ cookiecutter.version }}
dev:
	docker run -p 8080:8080 --rm -it {{ cookiecutter.project_slug}}:{{ cookiecutter.version }}
