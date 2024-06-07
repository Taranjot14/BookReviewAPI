from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_review_api.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    book = db.relationship('Book', backref=db.backref('reviews', lazy=True))
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

# Routes
@app.route("/")
def home():
    return "Book Review API"

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(email=data['email'], password=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "User already exists"}), 409

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/books", methods=["GET", "POST"])
@jwt_required()
def manage_books():
    if request.method == "POST":
        data = request.get_json()
        new_book = Book(title=data['title'], author=data['author'])
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message": "Book added", "book_id": new_book.id}), 201

    books = Book.query.all()
    return jsonify([{"id": book.id, "title": book.title, "author": book.author} for book in books]), 200

@app.route("/reviews/<int:book_id>", methods=["GET", "POST"])
@jwt_required()
def manage_reviews(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == "POST":
        data = request.get_json()
        user_id = get_jwt_identity()
        new_review = Review(book_id=book.id, user_id=user_id, content=data['content'])
        db.session.add(new_review)
        db.session.commit()
        return jsonify({"message": "Review added", "review_id": new_review.id}), 201

    reviews = Review.query.filter_by(book_id=book_id).all()
    return jsonify([{"id": review.id, "content": review.content, "user_id": review.user_id} for review in reviews]), 200

if __name__ == "__main__":
    db.create_all()  
    app.run(debug=True)
