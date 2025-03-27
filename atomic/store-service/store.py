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

class Store(db.Model):
    __tablename__ = 'Store'
    store_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pickup_location = db.Column(db.Integer, nullable=False)

@app.route('/store/<int:store_id>', methods=['GET'])
def get_store(store_id):
    store = Store.query.get(store_id)
    if store:
        return jsonify({"store_id": store.store_id, "pickup_location": store.pickup_location})
    return jsonify({"error": "Store not found"}), 404

@app.route('/store', methods=['GET'])
def get_all_stores():
    stores = Store.query.all()
    if stores:
        return jsonify({"store": [
            {"store_id": s.store_id, "pickup_location": s.pickup_location} 
            for s in stores
        ]})
    return jsonify({"error": "No stores found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)