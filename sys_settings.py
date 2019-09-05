import os

sentry_dsn = os.environ['SENTRY_DSN']
dev_post_gress_db = os.environ['HEROKU_PG_DEV']
prod_post_gress_db = os.environ['HEROKU_PG_PROD']
