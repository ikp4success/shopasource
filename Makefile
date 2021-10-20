# env
VENV := .venv
VENV_ACTIVATE := $(VENV)/bin/activate
VENV_SENTINEL := $(VENV)/.sentinel
VENV_PIP := $(VENV)/bin/pip $(PIP_EXTRA_OPTS)
VENV_AWS := $(VENV)/bin/aws
VENV_PRECOMMIT := $(VENV)/bin/pre-commit
VENV_PYTEST := $(VENV)/bin/pytest

STAGE ?= debug
PORT := 5003
HOST := 0.0.0.0
QUART_ENV := $(STAGE)
QUART_APP := webapp.app

DK_NAME ?= shopasource-psql
DB_PASS ?= admin
DB_USER ?= admin
DB_PORT ?= 5432
DB_NAME ?= shopasource
DB_DOMAIN ?= localhost

SAVE_TO_DB ?= 1
SEARCH_KEYWORD ?= wallet


.PHONY: ensure_git_clean
ensure_git_clean:
	@echo This target requires a clean git state, please stash or commit your changes if this fails on the next line
	test -z "$$(git status --porcelain)"


.PHONY: ensure_no_venv
ensure_no_venv:
ifdef VIRTUAL_ENV
	$(error Please deactivate your current virtual env)
endif


.PHONY: $(VENV)
$(VENV):
	$(MAKE) $(VENV_SENTINEL)


$(VENV_SENTINEL): requirements.txt .pre-commit-config.yaml
	$(MAKE) ensure_no_venv
	rm -rf $(VENV)
	python3.8 -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip wheel
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PRECOMMIT) install
	touch $(VENV_SENTINEL)


.PHONY: pre-commit
pre-commit: $(VENV_SENTINEL)
	$(VENV_PRECOMMIT) run -a


.PHONY: run
run:
	. $(VENV_ACTIVATE) ;\
	QUART_ENV=$(QUART_ENV) \
	QUART_APP=$(QUART_APP) \
	ENV_CONFIGURATION=$(STAGE) \
	SKIP_SENTRY=1 \
	STAGE=$(STAGE) \
	DB_USER=$(DB_USER) \
	DB_PASS=$(DB_PASS) \
	DB_PORT=$(DB_PORT) \
	DB_NAME=$(DB_NAME) \
	DB_DOMAIN=$(DB_DOMAIN) \
	SAVE_TO_DB=$(SAVE_TO_DB) \
	quart run --host=$(HOST) --port=$(PORT)


.PHONY: run_db
run_db:
	docker run --name $(DK_NAME) \
    -e POSTGRES_PASSWORD=$(DB_PASS) \
    -e POSTGRES_USER=$(DB_USER) \
    -e POSTGRES_DB=$(DB_NAME) \
    -p $(DB_PORT):$(DB_PORT) \
    -d postgres

.PHONY: stop_db
stop_db:
	docker stop $(DK_NAME)

.PHONY: clean_db
clean_db: stop_db
	docker rm $(DK_NAME)


.PHONY: load_db
load_db:
	psql postgresql://$(DB_USER):$(DB_PASS)@localhost:$(DB_PORT)/$(DB_NAME)


.PHONY: run_spider
run_spider:
	. $(VENV_ACTIVATE) ;\
	SAVE_TO_DB=0 \
	ENV_CONFIGURATION=$(STAGE) \
	SKIP_SENTRY=1 \
	STAGE=$(STAGE) \
	DB_USER=$(DB_USER) \
	DB_PASS=$(DB_PASS) \
	DB_PORT=$(DB_PORT) \
	DB_NAME=$(DB_NAME) \
	DB_DOMAIN=$(DB_DOMAIN) \
	$(VENV)/bin/scrapy crawl $(SPIDER) -a search_keyword=$(SEARCH_KEYWORD) -o json_shop_results/$(SPIDER)_RESULTS.json


.PHONY: docker_build
docker_build: docker_build
	docker build -t shopasource . \

.PHONY: run_docker
run_docker: docker_build
	docker run -it --net=host \
	  -e QUART_ENV=$(QUART_ENV) \
		-e QUART_APP=$(QUART_APP) \
		-e ENV_CONFIGURATION=$(STAGE) \
		-e SKIP_SENTRY=1 \
		-e STAGE=$(STAGE) \
		-e DB_USER=$(DB_USER) \
		-e DB_PASS=$(DB_PASS) \
		-e DB_PORT=$(DB_PORT) \
		-e DB_NAME=$(DB_NAME) \
		-e DB_DOMAIN=$(DB_DOMAIN) \
		-e SAVE_TO_DB=$(SAVE_TO_DB) \
		-p $(PORT):$(PORT) \
		shopasource


clean:
	rm -rf $(VENV)
	docker rm $(DK_NAME)
	docker image prune -f
	docker container prune


.PHONY: generate_key
generate_key: $(VENV)
	. $(VENV_ACTIVATE) ;\
	python -c 'from support import generate_key; print(generate_key())'
