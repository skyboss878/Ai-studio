from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    trial_start = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    subscribed = db.Column(db.Boolean, default=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "User already exists"}), 409
    user = User(email=data['email'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)
    return jsonify({"token": token})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"token": token})

@app.route('/subscription/activate', methods=['POST'])
@jwt_required()
def activate_subscription():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    user.subscribed = True
    db.session.commit()
    return jsonify({"msg": "Subscription activated"})

@app.route('/status', methods=['GET'])
@jwt_required()
def status():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    trial_end = user.trial_start + datetime.timedelta(days=3)
    trial_active = datetime.datetime.utcnow() < trial_end
    return jsonify({"trial": trial_active, "subscribed": user.subscribed})

if __name__ == '__main__':
    app.run(debug=True)