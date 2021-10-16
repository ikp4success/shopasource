#
# ShopASource Dockerfile
#
# http://www.shopasource.com
# Written by: Immanuel George <ikp4success@gmail.com>
#
# Usage:
#
#   sudo docker build -t shopasource .
#   sudo docker run -it -p 5003:5003 shopasource
#
# Pull the base image.
FROM python:3.8
ENV .venv 1.0
COPY requirements.txt .

RUN pip install --upgrade pip && pip --no-cache-dir install -r requirements.txt

EXPOSE 5001
WORKDIR /
ADD . .
# Run the application.
CMD ["gunicorn", "-b", "0.0.0.0:5003", "webapp.app:webapp.app"]
