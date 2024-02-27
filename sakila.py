from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://localhost:3306/sakila'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db=SQLAlchemy(app)

customer = db.Table('customer', db.metadata, autoload=True, autoload_with=db.engine)

@app.route('/')
def index():
    results = db.session.query(customer).all()
    for r in results:
        print(r.name)
    return ''