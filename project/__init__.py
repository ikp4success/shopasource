from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# from twilio.twiml.messaging_response import MessagingResponse
# from utilities.DefaultResources import _resultRow, _errorMessage
# import os

app = Flask(__name__, template_folder='web_content')
# app.secret_key = os.environ["SECRET_KEY"]
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://pnbfokqboucplu:c86e7fce019b590ef1f91e1a1a142ff5c9355b1c3b7589df10954b1a803121f3@ec2-54-243-46-32.compute-1.amazonaws.com:5432/dai7u33frhg47j"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['DEBUG'] = True

db = SQLAlchemy(app)
