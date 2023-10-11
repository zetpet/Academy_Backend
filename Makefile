.DEFAULT_GOAL := help
PYTHONPATH = PYTHONPATH=./
TEST = $(PYTHONPATH) pytest --verbosity=2 --showlocals --log-level=DEBUG --strict-markers $(arg)
CODE = app tests

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test
test: ## Runs pytest with coverage
	$(TEST) --cov

.PHONY: test-fast
test-fast: ## Runs pytest with exitfirst
	$(TEST) --exitfirst

.PHONY: test-failed
test-failed: ## Runs pytest from last-failed
	$(TEST) --last-failed

.PHONY: test-cov
test-cov: ## Runs pytest with coverage report
	$(TEST) --cov --cov-report html

.PHONY: install
install: ## Install project
	poetry install

.PHONY: update
update: ## Update packages
	poetry update

.PHONY: run
run: ## Run the main app
	poetry run python app/main.py

.PHONY: lint
lint: ## Lint code
	black --check $(CODE)
	flake8 --jobs 4 --statistics --show-source $(CODE)
	pylint $(CODE)
	mypy $(CODE)
	pytest --dead-fixtures --dup-fixtures
	safety check --full-report
	bandit -c pyproject.toml -r $(CODE)
	poetry check

.PHONY: format
format: ## Formats all files
	poetry run autoflake --recursive --in-place --ignore-init-module-imports --remove-all-unused-imports $(CODE)
	poetry run isort $(CODE)
	poetry run black $(CODE)

.PHONY: clean
clean: ## Clean caches
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache

.PHONY: check
check: format lint test ## Format and lint code then run tests
