#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flasgger import Swagger

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL")
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # disable modifications to prevent money used
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299} # discard and replace connection to prevent timeout

db = SQLAlchemy(app)

# Initialize flasgger 
app.config['SWAGGER'] = {
    'title': 'Drone microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows retrieve and update of drones statuses'
}
swagger = Swagger(app)


class Drone(db.Model):
    __tablename__ = 'Drone' # database table name

    droneID = db.Column(db.Integer, primary_key=True)
    drone_status = db.Column(db.String(50), nullable=False)


    def __init__(self, droneID, status):
        self.droneID = droneID
        self.drone_status = status


    def json(self):
        return {"Drone ID": self.droneID, "status": self.drone_status}

@app.route("/drones")
def get_all():
    """
    Get all drones with its statuses
    ---
    responses:
        200:
            description: Return all drones with its statuses
        404:
            description: No drones

    """

    dronelist = db.session.scalars(db.select(Drone)).all()

    if len(dronelist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "drones": [drone.json() for drone in dronelist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no drones."
        }
    ), 404

@app.route("/drone/<int:drone_id>", methods=['PUT'])
def update_order(drone_id):
    try:
        drone = db.session.scalar(db.select(Drone).filter_by(droneID=drone_id))
        if not drone:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "drone_id": drone_id
                    },
                    "message": "Drone not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data['status']:
            drone.drone_status = data['status']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": drone.json()
                }
            ), 200
    except Exception as e:
        print("Error: {}".format(str(e)))
        return jsonify(
            {
                "code": 500,
                "data": {
                    "drone_id": drone_id
                },
                "message": "An error occurred while updating Drone status. " + str(e)
            }
        ), 500
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)