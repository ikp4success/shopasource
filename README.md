# SHOP A SOURCE

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://github.com/timothycrosley/isort)
[![bandit](https://github.com/PyCQA/bandit/workflows/Build%20and%20Test%20Bandit/badge.svg)](https://github.com/PyCQA/bandit)


**Website**

https://shopasource.herokuapp.com/

**API**

https://github.com/ikp4success/shopasource/blob/master/api.md

**About**

Shop A Source provide easy access to search multiple shopping websites via one source. Website users can manage products and decide what product is best. Shop A Source could also be used to compare prices of a product.

**Screenshots**

![s1](https://github.com/ikp4success/shopasource/blob/master/screenshots/s1.png)
![s2](https://github.com/ikp4success/shopasource/blob/master/screenshots/s2.png)
![s3](https://github.com/ikp4success/shopasource/blob/master/screenshots/s3.png)


Hybrid of: https://github.com/ikp4success/bestlows-java

#### Python Version: 3.8+

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
project currently runs on Heroku, you can setup your own app-instance and deploy. for more information go to https://devcenter.heroku.com/articles/git. You could also use another service to host the project.

##### other
```bash
$ make generate_key
```


**Author**
[***Immanuel George***](https://stackoverflow.com/cv/imgeorgeresume)
