init_repo:
	@echo "Getting latest version of repository"
	git fetch && git pull
	@echo "Setting default commit template"
	git config --local commit.template .github/ct.md
