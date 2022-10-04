build:
	poetry build 
build_image:
	docker build . -t inference-engine:latest

publish:
	docker tag inference-engine:latest tiencheng/inference-engine:latest
	docker push tiencheng/inference-engine:latest
