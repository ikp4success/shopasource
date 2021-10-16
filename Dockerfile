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

EXPOSE 5003
WORKDIR /
ADD . .
# Run the application.
CMD ["quart", "run", "--host=0.0.0.0", "--port=5003"]
