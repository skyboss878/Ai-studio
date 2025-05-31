
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    joined = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    subscription_active = db.Column(db.Boolean, default=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify(message="User registered"), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        access_token = create_access_token(identity=user.username)
        return jsonify(access_token=access_token), 200
    return jsonify(message="Invalid credentials"), 401

@app.route('/generate-video', methods=['POST'])
@jwt_required()
def generate_video():
    user = get_jwt_identity()
    return jsonify(message="Video generation endpoint called by user: " + user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
