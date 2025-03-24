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
from sqlalchemy import text

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/my_database"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class Order(db.Model):
    __tablename__ = 'Order'
    __table_args__ = {'quote': True}  # Add this to handle case-sensitive table names

    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'Customer.Customer_ID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    drone_id = db.Column(db.Integer, db.ForeignKey(
        'Drone.DroneID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2))
    payment_status = db.Column(db.Boolean)
    deliveryLocation = db.Column(db.Integer)
    order_status = db.Column(db.String(255))

    def json(self):
        dto = {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'order_date': self.order_date,
            'drone_id': self.drone_id,
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
    __table_args__ = {'quote': True}  # Add this to handle case-sensitive table names

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.ForeignKey(
        'Order.order_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey(
        'Item.item_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

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
    customer_id = request.json.get('customer_id', None)
    order = Order(customer_id=customer_id, order_status='PENDING FOR DRONE')

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
        query = text("SELECT * FROM `Order` WHERE Order_ID = :order_id")
        result = db.session.execute(query, {"order_id": order_id})
        order_data = result.fetchone()
        
        if not order_data:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "order_id": order_id
                    },
                    "message": "Order not found."
                }
            ), 404

        # update status using raw SQL
        data = request.get_json()
        if data.get('status'):
            update_query = text("UPDATE `Order` SET Order_Status = :status WHERE Order_ID = :order_id")
            db.session.execute(update_query, {"status": data['status'], "order_id": order_id})
            db.session.commit()
            
            # Get the updated order for response
            result = db.session.execute(query, {"order_id": order_id})
            updated_order = result.fetchone()
            
            # Create a response JSON format
            order_json = {
                "order_id": updated_order.Order_ID,
                "order_date": updated_order.Order_Date.strftime("%Y-%m-%d %H:%M:%S") if updated_order.Order_Date else None,
                "drone_id": updated_order.Drone_ID,
                "total_amount": float(updated_order.Total_Amount) if updated_order.Total_Amount else None,
                "payment_status": updated_order.Payment_Status,
                "deliveryLocation": updated_order.DeliveryLocation,
                "customer_id": updated_order.Customer_ID,
                "order_status": updated_order.Order_Status
            }
            
            return jsonify(
                {
                    "code": 200,
                    "data": order_json
                }
            ), 200
        return jsonify(
            {
                "code": 400,
                "message": "No status provided in request."
            }
        ), 400
    except Exception as e:
        print("Error: {}".format(str(e)))
        return jsonify(
            {
                "code": 500,
                "data": {
                    "order_id": order_id
                },
                "message": "An error occurred while updating the order. " + str(e)
            }
        ), 500


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
                    "code": 400,
                    "message": "Invalid request. Please provide item_id and quantity."
                }
            ), 400

        new_item = Order_Item(
            order_id=order_id,
            item_id=item_data['item_id'],
            quantity=item_data['quantity']
        )
        
        db.session.add(new_item)
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
