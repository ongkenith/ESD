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

class Drone(db.Model):
    __tablename__ = 'Drone'
    
    droneID = db.Column(db.Integer, primary_key=True)
    Drone_Status = db.Column(db.String(50))

# Main Scheduling model
class Scheduling(db.Model):
    __tablename__ = 'scheduling'

    Schedule_ID = db.Column(db.Integer, primary_key=True)
    ScheduleDateTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    WeatherCheck = db.Column(db.Boolean, nullable=False)

    # Foreign key columns (for database relationships)
    store_id = db.Column(db.Integer, nullable=False)  # References store.store_id
    order_id = db.Column(db.Integer, nullable=False)  # References order.order_id
    droneID = db.Column(db.Integer, nullable=False)  # References drone.droneID
    
    # Actual location columns (for operational use)
    actual_pickup_location = db.Column(db.Integer, nullable=False)
    actual_delivery_location = db.Column(db.Integer, nullable=False)
    
    # Define foreign keys as relationships
    store = db.relationship('Store', foreign_keys=[store_id])
    order = db.relationship('Order', foreign_keys=[order_id])
    drone = db.relationship('Drone', foreign_keys=[droneID])
    
    # Specify all foreign key constraints with proper table and column names
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['store_id'], 
            ['Store.store_id'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        db.ForeignKeyConstraint(
            ['order_id'], 
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
        {'quote': True}
    )

    def json(self):
        dto = {
            'schedule_id': self.Schedule_ID,
            'schedule_date': self.ScheduleDateTime,
            'drone_id': self.droneID,
            'locations': {
                'pickup': {
                    'store_id': self.store_id,
                    'actual_location': self.actual_pickup_location
                },
                'delivery': {
                    'order_id': self.order_id,
                    'actual_location': self.actual_delivery_location
                }
            },
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
    try:
        data = request.json
        drone_id = data.get('drone_id')
        store_id = data.get('store_id')  # For foreign key
        order_id = data.get('order_id')  # For foreign key
        actual_delivery_location = data.get('deliveryLocation')  # Actual postal code
        actual_pickup_location = data.get('pickUpLocation')  # Actual postal code
        weather_check = data.get('weatherCheck')
        
        if not all([drone_id, store_id, order_id, actual_delivery_location, actual_pickup_location]):
            return jsonify({
                "code": 400,
                "message": "Missing required fields"
            }), 400

        # Create schedule with both reference IDs and actual locations
        schedule = Scheduling(
            droneID=drone_id,
            store_id=store_id,  # Foreign key to store
            order_id=order_id,  # Foreign key to order
            actual_pickup_location=actual_pickup_location,  # Actual pickup location
            actual_delivery_location=actual_delivery_location,  # Actual delivery location
            WeatherCheck=weather_check
        )

        db.session.add(schedule)
        db.session.commit()

        return jsonify({
            "code": 201,
            "data": schedule.json(),
            "message": "Schedule created successfully"
        }), 201

    except Exception as e:
        print("Error: {}".format(str(e)))
        return jsonify({
            "code": 500,
            "message": "An error occurred while creating the schedule. " + str(e)
        }), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5005, debug=True)