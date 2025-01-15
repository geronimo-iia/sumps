# const
.DEFAULT_GOAL := help

# MAIN TASKS ##################################################################

.PHONY: help
help: all
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# PROJECT DEPENDENCIES ########################################################

.PHONY: install
install: lock ## Install project dependencies
	@mkdir -p .cache
	uv venv
	uv pip install -r pyproject.toml --extra serializer


lock: pyproject.toml
	uv lock
	@touch $@
