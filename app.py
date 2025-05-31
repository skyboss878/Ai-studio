import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_PLAN_ID = os.getenv("PAYPAL_PLAN_ID")
BACKEND_URL = os.getenv("BACKEND_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

from flask import Flask, request, jsonify from flask_cors import CORS from flask_sqlalchemy import SQLAlchemy from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity import os import datetime import openai

app = Flask(name) CORS(app)

Environment Variables

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db') app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key') openai.api_key = os.getenv("OPENAI_API_KEY")

Extensions

db = SQLAlchemy(app) jwt = JWTManager(app)

User Model

class User(db.Model): id = db.Column(db.Integer, primary_key=True) email = db.Column(db.String(120), unique=True, nullable=False) password = db.Column(db.String(120), nullable=False) subscribed = db.Column(db.Boolean, default=False) signup_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

Create tables

with app.app_context(): db.create_all()

Routes

@app.route('/') def home(): return "AI Creators Studio Backend Running"

@app.route('/signup', methods=['POST']) def signup(): data = request.get_json() email = data['email'] password = data['password']

if User.query.filter_by(email=email).first():
    return jsonify({"message": "Email already exists"}), 409

new_user = User(email=email, password=password)
db.session.add(new_user)
db.session.commit()

return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST']) def login(): data = request.get_json() email = data['email'] password = data['password']

user = User.query.filter_by(email=email, password=password).first()

if not user:
    return jsonify({"message": "Invalid credentials"}), 401

access_token = create_access_token(identity=email)
return jsonify({"access_token": access_token, "subscribed": user.subscribed})

@app.route('/update-subscription', methods=['POST']) @jwt_required() def update_subscription(): current_user_email = get_jwt_identity() user = User.query.filter_by(email=current_user_email).first() if user: user.subscribed = True db.session.commit() return jsonify({"message": "Subscription updated"}) return jsonify({"message": "User not found"}), 404

@app.route('/generate-video', methods=['POST']) @jwt_required() def generate_video(): data = request.get_json() prompt = data.get('prompt')

if not prompt:
    return jsonify({"message": "Prompt required"}), 400

try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a viral video creator. Your job is to create short viral video scripts with music suggestions and trending hashtags."},
            {"role": "user", "content": prompt}
        ]
    )

    output = response['choices'][0]['message']['content']
    return jsonify({"videoScript": output})

except Exception as e:
    return jsonify({"message": "Error generating video", "error": str(e)}), 500

if name == 'main': app.run(debug=True)

