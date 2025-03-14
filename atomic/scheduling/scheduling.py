#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/my_database"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class Scheduling(db.Model):
    __tablename__ = 'Scheduling'

    schedule_id = db.Column(db.Integer, primary_key=True)
    scheduleName = db.Column(db.String(255), nullable=False)
    scheduleDateTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    droneID = db.Column(db.Integer, db.ForeignKey(
        'Drone.droneID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    deliveryLocation = db.Column(db.Integer, db.ForeignKey(
        'Order.deliveryLocation', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    pickUpLocation = db.Column(db.Integer, db.ForeignKey(
        'Store.pickup_location', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    weatherCheck = db.Column(db.Boolean, nullable=False)

    def json(self):
        dto = {
            'schedule_id': self.schedule_id,
            'schedule_name': self.scheduleName,
            'schedule_date': self.scheduleDateTime,
            'drone_id': self.droneID,
            'deliveryLocation': self.deliveryLocation,
            'pickUpLocation': self.pickUpLocation,
            'weatherCheck': self.weatherCheck
        }
        return dto



@app.route("/schedule/<string:drone_id>")
def find_by_drone_id(drone_id):
    schedule = db.session.scalar(db.select(Scheduling).filter_by(droneID=drone_id))
    if schedule:
        return jsonify(
            {
                "code": 200,
                "data": schedule.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "drone_id": drone_id
            },
            "message": "Drone not found."
        }
    ), 404

@app.route("/schedule", methods=['POST'])
def create_schedule():
    drone_id = request.json.get('drone_id')
    deliveryLocation = request.json.get('deliveryLocation')
    pickUpLocation = request.json.get('pickUpLocation')
    weatherCheck = request.json.get('weatherCheck')
    schedule = Scheduling(droneID=drone_id, scheduleName='STH STH STH', deliveryLocation=deliveryLocation, pickUpLocation=pickUpLocation, weatherCheck=weatherCheck)

    try:
        db.session.add(schedule)
        db.session.commit()
    except Exception as e:
        print("Error: {}".format(str(e)))
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": schedule.json()
        }
    ), 201


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
