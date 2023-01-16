start-dev-cluster:
	sh k8s/environments/development/cluster/generate-ip-address-pool-kind.sh &&	kind create cluster --config k8s/environments/development/cluster/kind.yaml
remove-dev-cluster:
	kind delete cluster
reset-dev-cluster:
	make remove-dev-cluster && make start-dev-cluster 
k8s-dev:
	skaffold dev --force
k8s-run:
	skaffold run --force
generate-k8s-dashboard-token:
	kubectl -n kubernetes-dashboard create token admin-user --duration=488h > token.txt
install-precommit:
	@echo "Installing precommit hook"
	pre-commit install
