# SHOP A SOURCE

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://github.com/timothycrosley/isort)
[![bandit](https://github.com/PyCQA/bandit/workflows/Build%20and%20Test%20Bandit/badge.svg)](https://github.com/PyCQA/bandit)


**Website**

http://www.shopasource.com/

**About**

Shop A Source provide easy access to search multiple shopping websites via one source. Website users can manage products and decide what product is best. Shop A Source could also be used to compare prices of a product.

**ScreenShots**

![s1](https://github.com/ikp4success/shopasource/blob/master/screenshots/s1.png)
![s2](https://github.com/ikp4success/shopasource/blob/master/screenshots/s2.png)
![s3](https://github.com/ikp4success/shopasource/blob/master/screenshots/s3.png)

**Technologies**

Python,
Html,
Flask,
Heroku,
Postgres,
sqlalchemy
JavaScript
Css

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

Update values in configs/dev for dev environment and deploy's.


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

##### run individual spider
```bash
$ make run_spider SPIDER=AMAZON SEARCH_KEYWORD=shirts
```


**API**

http://www.shopasource.com/api


**Author**
[***Immanuel George***](https://stackoverflow.com/cv/imgeorgeresume)
