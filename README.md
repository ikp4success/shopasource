# SHOP A SOURCE

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://github.com/timothycrosley/isort)
[![bandit](https://github.com/PyCQA/bandit/workflows/Build%20and%20Test%20Bandit/badge.svg)](https://github.com/PyCQA/bandit)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97757.svg)](https://claude.com/claude-code)
[![Built with Codex](https://img.shields.io/badge/Built%20with-Codex-000000.svg?logo=openai&logoColor=white)](https://openai.com/codex/)
[![Built with Mistral Vibe](https://img.shields.io/badge/Built%20with-Mistral%20Vibe-7746DC.svg)](https://mistral.ai/)
[![AI-powered search](https://img.shields.io/badge/search-AI--powered-6366f1.svg)](https://github.com/ikp4success/shopasource/blob/master/api.md)

**API**

https://github.com/ikp4success/shopasource/blob/master/api.md

**About**

Shop A Source lets you search for a product in plain English and compares prices for it
across dozens of online stores in one place. Describe what you're looking for - "cheap
waterproof hiking boots from target" - and an LLM (Claude, GPT/Codex, Gemini, DeepSeek, Groq,
or Mistral - pick whichever the server has a key for) works out the shops, sorting, and
filters for you.

**Screenshots**

![s1](https://github.com/ikp4success/shopasource/blob/master/screenshots/s1.png)
![s2](https://github.com/ikp4success/shopasource/blob/master/screenshots/s2.png)
![s3](https://github.com/ikp4success/shopasource/blob/master/screenshots/s3.png)


Hybrid of: https://github.com/ikp4success/bestlows-java

#### Python Version: 3.13+ (Quart>=0.23.1 requires it)

### Setup

```bash
$ make .venv
$ make clean # cleans virtual environment folder
```
Setup virtual environment

### Pre-commit

[pre-commit](https://pre-commit.com/) installed automatically via .venv, used for linting best practices.

```bash
$ make pre-commit
```

#### Settings

* Update values in configs/dev for dev environment and deploy's.
* A template dev.json.template is provided to setup a dev.json config files.
* Use debug.json for debugging and testing.
* dev.json is git-ignored to protect sensitive keys.
* For natural-language search, set at least one of ANTHROPIC_API_KEY, OPENAI_API_KEY,
  GEMINI_API_KEY, DEEPSEEK_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY. With more than one
  set, LLM_PROVIDER picks the default, and the UI lets a user override it per search
  from whichever are configured. Gemini automatically falls back through older
  free-tier models if the current one is out of quota, retired, or overloaded.



##### run flask project
```bash
$ make run STAGE=debug or make run  # debug is default

$ make run STAGE=dev # dev runs
```

##### setup docker db for debug runs
Assumes docker is installed on machine.
```bash
$ make run_db
$ make clean_db
$ make stop_db

$ make load_db # psql interactive db shell
```

##### run flask project in docker
```bash
$ make run_docker  # debug is default
# make sure db is running or ..
$ make run_db && make run_docker
```

##### run individual spider
```bash
$ make run_spider SPIDER=AMAZON SEARCH_KEYWORD=shirts
```

##### deploys
The repository includes a Render Blueprint that deploys the Docker image and a
PostgreSQL database together. Push the repository, choose **New > Blueprint** in
Render, and select the repository. Render reads `render.yaml`, generates the API
key, connects `DATABASE_URL`, and checks `/health` automatically.

The LLM API keys are optional. Add any of `GEMINI_API_KEY`, `GROQ_API_KEY`,
`MISTRAL_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or
`DEEPSEEK_API_KEY` from the service's **Environment** page. Free Render PostgreSQL
databases expire after 30 days, so use a paid database for persistent production
data.

The `Procfile` remains available for Heroku or another host that supports it.

##### other
```bash
$ make generate_key
```


**Author**

* [***Immanuel George***](https://www.linkedin.com/in/imgeorgeresume/)
