import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from models import User

scan_bp = Blueprint('scan', __name__)

UPLOAD_FOLDER = 'uploads/'  # Directory to store scanned documents
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Document Scanning & Upload API
@scan_bp.route('/api/scan', methods=['POST'])
@jwt_required()
def scan_document():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.credits < 1:
        return jsonify({'error': 'Insufficient credits'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    user.deduct_credits(1)  # Deduct 1 credit per scan
    
    return jsonify({'message': 'Scan successful, 1 credit deducted', 'remaining_credits': user.credits, 'file_url': filepath}), 200

# ✅ Retrieve Scanned Document API
@scan_bp.route('/api/scan/<filename>', methods=['GET'])
@jwt_required()
def get_scanned_document(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
