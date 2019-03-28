#
# ShopASource Dockerfile
#
# http://www.shopasource.com
# Written by: Immanuel George <ikp4success@gmail.com>
#
# Usage:
#
#   sudo docker build -t shopasource .
#   sudo docker run -p 127.0.0.1:5001:5001 shopasource
#
# Pull the base image.
FROM python:3
ENV proj_env_shop_a_source 1.0
COPY requirements.txt .

RUN pip install --upgrade pip && pip --no-cache-dir install -r requirements.txt

EXPOSE 5001
WORKDIR /
ADD . .
# Run the application.
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]
