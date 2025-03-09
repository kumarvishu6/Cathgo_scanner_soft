import os

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Store files in 'uploads' directory
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Config (Modify if needed)
SQLALCHEMY_TRACK_MODIFICATIONS = False
