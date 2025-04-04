#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os
from flasgger import Swagger
from sqlalchemy import text, MetaData

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

db = SQLAlchemy(app)

class Customer(db.Model):
    __tablename__ = 'Customer'
    Customer_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Mobile_No = db.Column(db.String(8), nullable=False)

class Drone(db.Model):
    __tablename__ = 'Drone' # database table name

    droneID = db.Column(db.Integer, primary_key=True)
    drone_status = db.Column(db.String(50), nullable=False)

class Item(db.Model):
    __tablename__ = 'Item'
    Item_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    store_id = db.Column(db.String(255), nullable=False)
    Price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __tablename__ = 'Order'

    order_id = db.Column(db.Integer, primary_key=True)
    Customer_ID = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    droneID = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2))
    payment_status = db.Column(db.Boolean)
    deliveryLocation = db.Column(db.Integer)
    order_status = db.Column(db.String(255))

    __table_args__ = (
        db.ForeignKeyConstraint(
            ['droneID'], 
            ['Drone.droneID'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ), 
        db.ForeignKeyConstraint(
            ['Customer_ID'], 
            ['Customer.Customer_ID'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ), 
    {'quote': True})  # Add this to handle case-sensitive table names

    def json(self):
        dto = {
            'order_id': self.order_id,
            'Customer_ID': self.Customer_ID,
            'order_date': self.order_date,
            'drone_id': self.droneID,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'deliveryLocation': self.deliveryLocation,
            'order_status': self.order_status
        }

        dto['order_item'] = []
        for oi in self.order_item:
            dto['order_item'].append(oi.json())

        return dto


class Order_Item(db.Model):
    __tablename__ = 'Order_Item'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False, index=True)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.ForeignKeyConstraint(
            [item_id], 
            ['Item.Item_ID'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        db.ForeignKeyConstraint(
            [order_id], 
            ['Order.order_id'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
    {'quote': True})  # Add this to handle case-sensitive table names

    # order_id = db.Column(db.String(36), db.ForeignKey('order.order_id'), nullable=False)
    # order = db.relationship('Order', backref='order_item')
    order = db.relationship(
        'Order', primaryjoin='Order_Item.order_id == Order.order_id', backref='order_item')

    def json(self):
        return {'item_id': self.item_id, 'quantity': self.quantity, 'order_id': self.order_id}


@app.route("/order")
def get_all():
    orderlist = db.session.scalars(db.select(Order)).all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404


@app.route("/order/<string:order_id>")
def find_by_order_id(order_id):
    order = db.session.scalar(db.select(Order).filter_by(order_id=order_id))
    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "order_id": order_id
            },
            "message": "Order not found."
        }
    ), 404


@app.route("/order", methods=['POST'])
def create_order():
    Customer_ID = request.json.get('Customer_ID', None)
    total_amount = request.json.get('total_amount', 0)
    delivery_location = request.json.get('delivery_location', 000000)
    order = Order(Customer_ID=Customer_ID, order_status='PENDING FOR DRONE', total_amount=total_amount, deliveryLocation=delivery_location, payment_status=False)

    cart_item = request.json.get('cart_item')
    for item in cart_item:
        order.order_item.append(Order_Item(
            item_id=item['item_id'], quantity=item['quantity']))

    try:
        db.session.add(order)
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
            "data": order.json()
        }
    ), 201


@app.route("/order/<string:order_id>", methods=['PUT'])
def update_order(order_id):
    try:
        # Try to get the order using raw SQL to bypass ORM foreign key constraints
        # First check if the order exists
        # changed this to fit postgresql format
        order = db.session.scalar(db.select(Order).filter_by(order_id=order_id))
        
        if not order:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "order_id": order_id
                    },
                    "message": "Order not found."
                }
            ), 404
        
        data = request.get_json()
        if not data:
            return jsonify(
                {
                    "code": 401,
                    "message": "No data provided in request."
                }
            ), 401

        # update status using raw SQL
        
        # Update fields if provided
        if 'status' in data:
            order.order_status = data['status']
        if 'drone_id' in data:
            order.droneID = data['drone_id']

        try:
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": order.json()
                }
            ), 200
        except Exception as e:
            db.session.rollback()
            return jsonify(
                {
                    "code": 501,
                    "message": f"Database error: {str(e)}"
                }
            ), 501

    except Exception as e:
        print("Error: {}".format(str(e)))
        return jsonify(
            {
                "code": 502,
                "data": {
                    "order_id": order_id
                },
                "message": "An error occurred while updating the order. " + str(e)
            }
        ), 502

@app.route("/order/<string:order_id>/add_item", methods=['POST'])
def add_item_to_order(order_id):
    try:
        order = db.session.scalar(db.select(Order).filter_by(order_id=order_id))
        if not order:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "order_id": order_id
                    },
                    "message": "Order not found."
                }
            ), 404

        # Add the item to the order
        item_data = request.json
        if not item_data or 'item_id' not in item_data or 'quantity' not in item_data:
            return jsonify(
                {
                    "code": 401,
                    "message": "Invalid request. Please provide item_id and quantity."
                }
            ), 401

        new_item = Order_Item(
            order_id=order_id,
            item_id=item_data['item_id'],
            quantity=item_data['quantity']
        )
        
        order.order_item.append(new_item)

        db.session.commit()
        
        return jsonify(
            {
                "code": 201,
                "data": {
                    "order_id": order_id,
                    "item_added": new_item.json()
                },
                "message": "Item added to order successfully."
            }
        ), 201
    except Exception as e:
        print("Error: {}".format(str(e)))
        return jsonify(
            {
                "code": 500,
                "data": {
                    "order_id": order_id
                },
                "message": "An error occurred while adding item to the order. " + str(e)
            }
        ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5004, debug=True)
