from crypt import methods
import datetime
import json
from tkinter import NO
from unicodedata import name
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_expects_json import expects_json


app = Flask(__name__)

schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'description': {'type': 'string'},
        'size': {'type': 'string'},
        'color': {'type': 'string'},
    },
    'required': ['name', 'description', 'size', 'color']
}

app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost/sda_practica1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)
mar = Marshmallow(app)

class Clothes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(500))
    size = db.Column(db.String(255))
    color = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, name, description, size, color):
        self.name = name
        self.description = description
        self.size = size
        self.color = color

class ClothesSchema(mar.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'size', 'color')
    
clothe_schema = ClothesSchema()
clothes_schema = ClothesSchema(many=True)

@app.route('/clothes', methods=['POST'])
@expects_json(schema)
def create_clothe():
    name = request.json['name']
    description = request.json['description']
    size = request.json['size']
    color = request.json['color']

    new_clothe = Clothes(name, description, size, color)

    db.session.add(new_clothe)
    db.session.commit()

    return clothe_schema.jsonify(new_clothe)

@app.route('/clothes', methods=['GET'])
def get_clothes():
    all_clothes = Clothes.query.all()
    result = clothes_schema.dump(all_clothes)
    return jsonify(result)

@app.route('/clothes/<id>', methods=['GET'])
def get_clothe(id):
    clothe = Clothes.query.get(id)
    if clothe is None:
        return jsonify({"message": "Clothe not found"}), 404
    return clothe_schema.jsonify(clothe)

@app.route('/clothes/<id>', methods=['PUT'])
def update_clothe(id):
    clothe = Clothes.query.get(id)

    name = request.json['name'] if 'name' in request.json else clothe.name
    description = request.json['description'] if 'description' in request.json else clothe.description
    size = request.json['size'] if 'size' in request.json else clothe.size
    color = request.json['color'] if 'color' in request.json else clothe.color

    clothe.name = name
    clothe.description = description
    clothe.size = size
    clothe.color = color

    db.session.commit()

    return clothe_schema.jsonify(clothe) 

@app.route('/clothes/<id>', methods=['DELETE'])
def delete_clothe(id):
    clothe = Clothes.query.get(id)
    if clothe is None:
        return jsonify({'message': 'Not found'})

    db.session.delete(clothe)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)

