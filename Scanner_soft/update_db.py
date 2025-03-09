from app import create_app
from models import db
from sqlalchemy import text  # Import text

app = create_app()
with app.app_context():
    db.session.execute(text("UPDATE document SET file_type = 'pdf' WHERE file_type IS NULL;"))
    db.session.commit()

print("Database updated successfully!")
