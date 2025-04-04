from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from os import environ
import os

# Define a naming convention for the constraints to match MySQL's behavior
convention = {
  "ix": 'ix_%(column_0_label)s',
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL")
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app, metadata=metadata)


# Define a model for Order table
class Order(db.Model):
    __tablename__ = 'Order'  # We'll use __table_args__ to handle the quotes
    
    Order_ID = db.Column(db.Integer, primary_key=True)
    Order_Date = db.Column(db.DateTime, nullable=False)
    droneID = db.Column(db.Integer)
    Total_Amount = db.Column(db.Float)
    Payment_Status = db.Column(db.Boolean)
    deliveryLocation = db.Column(db.Integer)
    Customer_ID = db.Column(db.Integer)
    Order_Status = db.Column(db.String(255))
    
    __table_args__ = {'quote': True}  # This tells SQLAlchemy to quote the table name

# Define models for other tables needed for relationships
class Store(db.Model):
    __tablename__ = 'Store'
    
    store_id = db.Column(db.Integer, primary_key=True)
    pickup_location = db.Column(db.Integer, nullable=False)
    store_image_url = db.Column(db.Text)

class Drone(db.Model):
    __tablename__ = 'Drone'
    
    droneID = db.Column(db.Integer, primary_key=True)
    Drone_Status = db.Column(db.String(50))

# Main Scheduling model
class Scheduling(db.Model):
    __tablename__ = 'scheduling'  # Changed to lowercase to match the SQL schema

    Schedule_ID = db.Column(db.Integer, primary_key=True)  # Changed to match SQL case
    ScheduleName = db.Column(db.String(255), nullable=False)  # Changed to match SQL case
    ScheduleDateTime = db.Column(db.DateTime, nullable=False, default=datetime.now)  # Changed to match SQL case
    WeatherCheck = db.Column(db.Boolean, nullable=False)  # Changed to match SQL case

    # Define columns with matching case to SQL schema
    PickUpLocation = db.Column(db.Integer, nullable=False)  # Changed to match SQL case
    deliveryLocation = db.Column(db.Integer, nullable=False)  # Changed to match SQL case
    droneID = db.Column(db.Integer, nullable=False)  # Changed to match SQL case
    
    # Define foreign keys as relationships instead of constraints
    pickup_location = db.relationship('Store', foreign_keys=[PickUpLocation])
    delivery_location = db.relationship('Order', foreign_keys=[deliveryLocation])
    drone = db.relationship('Drone', foreign_keys=[droneID])
    
    # Specify all foreign key constraints with proper table and column names
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['PickUpLocation'], 
            ['Store.store_id'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        db.ForeignKeyConstraint(
            ['deliveryLocation'], 
            ['Order.Order_ID'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        db.ForeignKeyConstraint(
            ['droneID'], 
            ['Drone.droneID'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        {'quote': True}  # This tells SQLAlchemy to quote the table name and identifiers
    )

    def json(self):
        dto = {
            'schedule_id': self.Schedule_ID,
            'schedule_name': self.ScheduleName,
            'schedule_date': self.ScheduleDateTime,
            'drone_id': self.droneID,
            'deliveryLocation': self.deliveryLocation,
            'pickUpLocation': self.PickUpLocation,
            'weatherCheck': self.WeatherCheck
        }
        return dto
    
@app.route("/schedule")
def get_all_schedule():
    schedule = db.session.scalar(db.select(Scheduling))
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
            "message": "No schedule exists"
        }
    ), 404

@app.route("/schedule/<string:drone_id>")
def find_by_drone_id(drone_id):
    schedule = db.session.scalar(db.select(Scheduling).filter_by(droneID=int(drone_id)))
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
    
    # Updated to use the correct field names that match the database schema
    schedule = Scheduling(
        droneID=drone_id, 
        ScheduleName='STH STH STH', 
        deliveryLocation=deliveryLocation, 
        PickUpLocation=pickUpLocation, 
        WeatherCheck=weatherCheck
    )

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
    app.run(host='0.0.0.0', port=5005, debug=True)