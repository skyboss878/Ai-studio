from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
import os
import openai
from dotenv import load_dotenv
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the .env file

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("open_ai_key")
PAYPAL_PLAN_ID = os.getenv("PAYPAL_PLAN_ID")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Initialize app
app = Flask(__name__)
CORS(app)

# App configuration
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# User database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    trial_start = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    subscribed = db.Column(db.Boolean, default=False)

# Create DB tables once
@app.before_request
def before_request():
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True

# Home route
@app.route("/", methods=["GET"])
def home():
    return "✅ Welcome to AI Creators Studio API!"

# User Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
    password = data['password']
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'User already exists'}), 409
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User registered successfully'}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email, password=password).first()
    if not user:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    # Trial & subscription check
    days_since_trial = (datetime.datetime.utcnow() - user.trial_start).days
    if not user.subscribed and days_since_trial > 3:
        return jsonify({'success': False, 'message': 'Trial expired. Please subscribe.'}), 403

    token = create_access_token(identity=user.email)
    return jsonify({'success': True, 'token': token}), 200

# Viral Video Idea Generator
@app.route('/generate-idea', methods=['POST'])
@jwt_required()
def generate_idea():
    user_email = get_jwt_identity()
    data = request.get_json()
    prompt = data.get('prompt', '')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in viral short-form video marketing. Respond with a creative idea, hook, caption, and background music style for the given topic."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response['choices'][0]['message']['content']
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Viral Caption & Hashtag Generator
@app.route('/generate-caption-hashtags', methods=['POST'])
@jwt_required()
def generate_caption_hashtags():
    user_email = get_jwt_identity()
    data = request.get_json()
    topic = data.get('topic', '')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a viral social media expert. For the given topic, write a catchy caption and viral hashtags for TikTok, Reels, and Shorts."},
                {"role": "user", "content": topic}
            ]
        )
        result = response['choices'][0]['message']['content']
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Check if user is subscribed
@app.route('/check-subscription', methods=['POST'])
@jwt_required()
def check_subscription():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if user:
        return jsonify({'subscribed': user.subscribed})
    return jsonify({'error': 'User not found'}), 404

# Mark user as subscribed
@app.route('/mark-subscribed', methods=['POST'])
@jwt_required()
def mark_subscribed():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if user:
        user.subscribed = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Subscription updated'})
    return jsonify({'error': 'User not found'}), 404

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
