from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Customer(db.Model):
    __tablename__ = 'Customer'
    Customer_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Mobile_No = db.Column(db.String(8), nullable=False)

@app.route('/customers', methods=['GET'])
def get_all_customers():
    customers = Customer.query.all()
    if customers:
        return jsonify({"customers": [
            {"Customer_ID": c.Customer_ID, "Name": c.Name, "Email": c.Email, "Mobile_No": c.Mobile_No} 
            for c in customers
        ]})
    return jsonify({"error": "No customers found"}), 404

@app.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        return jsonify({"Customer_ID": customer.Customer_ID, "Name": customer.Name, "Email": customer.Email, "Mobile_No": customer.Mobile_No})
    return jsonify({"error": "Customer not found"}), 404

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    mobile_no = data.get('mobile_no')

    if not email or not mobile_no:
        return jsonify({"error": "Email and mobile number are required"}), 400

    customer = Customer.query.filter_by(Email=email, Mobile_No=mobile_no).first()
    
    if customer:
        return jsonify({
            "success": True,
            "customer": {
                "Customer_ID": customer.Customer_ID,
                "Name": customer.Name,
                "Email": customer.Email,
                "Mobile_No": customer.Mobile_No
            }
        }), 200
    else:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/registration', methods=['POST'])
def create_customer():
    name = request.json.get('name', "Rando Person")
    email = request.json.get('email', None)
    if email == None:
        return jsonify({"error": "Enter an email"}), 401
    mobile_number = request.json.get('mobile_number', 90000000)
    customer = Customer(Name=name, Email=email, Mobile_No=mobile_number)
    try:
        db.session.add(customer)
        db.session.commit()
    except Exception as e:
        print("Error: {}".format(str(e)))
        return jsonify(
            {
                "code": 500,
                "error": "An error occurred while creating the order. " + str(e)
            }
        ), 500
    return jsonify(
        {
            "message": "Registration completed!"
        }
    ), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)