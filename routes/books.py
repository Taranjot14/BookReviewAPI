from flask import Blueprint, request, jsonify
from app import db
from models import Book
from schemas.book import book_schema
from flask_jwt_extended import jwt_required

books_bp = Blueprint('books_bp', __name__)

@books_bp.route("/", methods=["GET", "POST"])
@jwt_required()
def manage_books():
    if request.method == "POST":
        data = request.get_json()
        errors = book_schema.validate(data)
        if errors:
            return jsonify(errors), 400
        new_book = Book(title=data['title'], author=data['author'], category=data['category'])
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message": "Book added", "book_id": new_book.id}), 201

    books = Book.query.all()
    return jsonify(book_schema.dump(books, many=True)), 200

@books_bp.route("/search", methods=["GET"])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"message": "No search query provided"}), 400

    books = Book.query.filter(
        (Book.title.ilike(f'%{query}%')) | 
        (Book.author.ilike(f'%{query}%')) |
        (Book.category.ilike(f'%{query}%'))
    ).all()
    return jsonify(book_schema.dump(books, many=True)), 200
