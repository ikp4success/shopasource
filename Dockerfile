#
# ShopASource Dockerfile
#
# Written by: Immanuel George <ikp4success@gmail.com>
#
# Usage:
#
#   sudo docker build -t shopasource .
#   sudo docker run -it -p 5003:5003 shopasource
#
# Pull the base image.
FROM python:3.13-slim

COPY requirements.txt .

RUN pip install --upgrade pip && pip --no-cache-dir install -r requirements.txt \
    && playwright install --with-deps chrome

EXPOSE 10000
WORKDIR /
ADD . .
# Run the application. `quart run` fails here (package discovery breaks on the
# stray root __init__.py) - run the ASGI app directly, matching the Procfile.
CMD ["sh", "-c", "hypercorn -b 0.0.0.0:${PORT:-5003} webapp.app:app"]
