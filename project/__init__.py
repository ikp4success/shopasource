import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# from twilio.twiml.messaging_response import MessagingResponse
# from utilities.DefaultResources import _resultRow, _errorMessage
# import os
app = Flask(__name__, template_folder='web_content')
hk_dev_db_uri = "postgres://pnbfokqboucplu:c86e7fce019b590ef1f91e1a1a142ff5c9355b1c3b7589df10954b1a803121f3@ec2-54-243-46-32.compute-1.amazonaws.com:5432/dai7u33frhg47j"
hk_pr_db_uri = "postgres://prlmhendyzlyjc:0bbb3d230e4f9b0c6e0ab7762c4598eaafc6359534d0c3636c336c788c32e2c5@ec2-54-243-223-245.compute-1.amazonaws.com:5432/dbtrd75qf6bcuv"
# app.secret_key = os.environ["SECRET_KEY"]
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
# app.config['SQLALCHEMY_DATABASE_URI'] = hk_dev_db_uri
if sys.argv and len(sys.argv) > 0 and "debug=True" in sys.argv:
    app.config['SQLALCHEMY_DATABASE_URI'] = hk_dev_db_uri
    app.config['DEBUG'] = True
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = hk_pr_db_uri
    app.config['DEBUG'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)
