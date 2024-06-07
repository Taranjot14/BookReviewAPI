from flask import Blueprint, request, jsonify
from app import db
from models import Book, Review
from schemas.review import review_schema
from flask_jwt_extended import jwt_required, get_jwt_identity

reviews_bp = Blueprint('reviews_bp', __name__)

@reviews_bp.route("/<int:book_id>", methods=["GET", "POST"])
@jwt_required()
def manage_reviews(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == "POST":
        data = request.get_json()
        errors = review_schema.validate(data)
        if errors:
            return jsonify(errors), 400
        user_id = get_jwt_identity()
        new_review = Review(book_id=book.id, user_id=user_id, content=data['content'], rating=data['rating'])
        db.session.add(new_review)
        db.session.commit()

        # Update book average rating
        book_reviews = Review.query.filter_by(book_id=book.id).all()
        avg_rating = sum(review.rating for review in book_reviews) / len(book_reviews)
        book.avg_rating = avg_rating
        db.session.commit()

        return jsonify({"message": "Review added", "review_id": new_review.id}), 201

    reviews = Review.query.filter_by(book_id=book_id).all()
    return jsonify(review_schema.dump(reviews, many=True)), 200
