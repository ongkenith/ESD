from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root:root@localhost:8889/my_database"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Item(db.Model):
    __tablename__ = 'Item'
    Item_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Store_ID = db.Column(db.String(255), nullable=False)
    Price = db.Column(db.Float, nullable=False)
    
@app.route('/items', methods=['GET'])
def get_all_items():
    items = Item.query.all()
    if items:
        return jsonify({"items": [
            {"Item_ID": i.Item_ID, "Name": i.Name, "Store_ID": i.Store_ID, "Price": i.Price} 
            for i in items
        ]})
    return jsonify({"error": "No items found"}), 404

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get(item_id)
    if item:
        return jsonify({"Item_ID": item.Item_ID, "Name": item.Name, "Store_ID": item.Store_ID, "Price": item.Price})
    return jsonify({"error": "Item not found"}), 404

@app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    new_item = Item(
        Name=data['Name'],
        Store_ID=data['Store_ID'],
        Price=data['Price']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"Item_ID": new_item.Item_ID, "Status": "Created"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)