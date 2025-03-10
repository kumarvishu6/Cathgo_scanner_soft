from app import create_app, db
from models import User, db
from werkzeug.security import generate_password_hash

#  Create the Flask app instance
app = create_app()

#  Run the script inside the app context
with app.app_context():
    existing_user = User.query.filter_by(email="test@example.com").first()
    
    if not existing_user:
        test_user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("password123", method='pbkdf2:sha256')
        )
        db.session.add(test_user)
        db.session.commit()
        print(" Test user added successfully.")
    else:
        print("ℹ Test user already exists.")
