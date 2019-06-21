"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import openaq
import os

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)
api = openaq.OpenAQ()


def get_date_and_measure(city, parameter):
    status, body = api.measurements(city=city, parameter=parameter)

    return [(result['date']['utc'], result['value'])
            for result in body['results']]


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '<Time {} --- Value {} >'.format(self.datetime, self.value)


@APP.route('/')
def root():
    records=list(DB.session.query(Record).filter(Record.value >= 10))
 


@APP.route('/refresh')
def refresh():
    DB.drop_all()
    DB.create_all()
    data = get_date_and_measure('Los Angeles', 'pm25')
    for item in data:
        record = Record(datetime=item[0], value=item[1])
        DB.session.add(record)
    DB.session.commit()
    return 'Data refreshed!'


