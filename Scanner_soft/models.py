from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from app import db  # Import db from app.py instead of creating a new instance

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    credits = db.Column(db.Integer, default=10)  # Default credits

    # ✅ Deduct credits when scanning a document
    def deduct_credits(self, amount):
        if self.credits >= amount:
            self.credits -= amount
            db.session.commit()
            return True  # Deduction successful
        return False  # Not enough credits

    # ✅ Add credits (Admin functionality)
    def add_credits(self, amount):
        self.credits += amount
        db.session.commit()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)  # Store file path
    file_type = db.Column(db.String(50), nullable=False)  # e.g., PDF, PNG, JPG
    file_size = db.Column(db.Integer, nullable=False)  # File size in KB
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(20), default="pending")  # pending, completed, failed
    content = db.Column(db.Text, nullable=True)  # ✅ Added this field for extracted text
    user = db.relationship('User', backref=db.backref('documents', lazy=True))

    # ✅ Mark document as processed
    def mark_processed(self, status="completed"):
        self.processing_status = status
        db.session.commit()
