import os
import fitz  
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import db, Document, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define the blueprint
document_bp = Blueprint('document_bp', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """ Extracts text from a PDF file using PyMuPDF. """
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text")  
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text.strip()

#  Document Upload API
@document_bp.route('/api/upload', methods=['POST'])
@jwt_required()  
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        file.save(file_path)  

        # Get user ID from JWT
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Extract file extension for file_type
        file_type = filename.rsplit('.', 1)[1].lower()

        # Extract text if it's a PDF
        extracted_text = extract_text_from_pdf(file_path) if file_type == 'pdf' else ""

        # Save to DB
        new_document = Document(
            user_id=user.id, 
            filename=filename, 
            file_path=file_path,
            file_type=file_type,  
            file_size=os.path.getsize(file_path),  # Save file size
            processing_status='completed' if file_type == 'pdf' else 'pending',
            content=extracted_text  # Store extracted text
        )
        db.session.add(new_document)
        db.session.commit()

        return jsonify({'message': 'File uploaded successfully', 'file': filename}), 201
    
    return jsonify({'error': 'Invalid file format'}), 400

#  Document Matching API
@document_bp.route('/api/match', methods=['POST'])
@jwt_required()
def match_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # Save file

        # Extract text
        file_type = filename.rsplit('.', 1)[1].lower()
        query_text = extract_text_from_pdf(file_path) if file_type == 'pdf' else ""
        
        if not query_text:
            return jsonify({'error': 'No text extracted from document'}), 400

        # Fetch all stored documents
        stored_docs = Document.query.filter(Document.processing_status == 'completed').all()
        stored_texts = [doc.content for doc in stored_docs]
        stored_filenames = [doc.filename for doc in stored_docs]

        if not stored_texts:
            return jsonify({'error': 'No documents available for comparison'}), 400

        # Compute similarity
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([query_text] + stored_texts)
        cosine_similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

        # Create response
        results = [
            {'filename': stored_filenames[i], 'similarity': float(cosine_similarities[i])}
            for i in range(len(stored_texts))
        ]
        results = sorted(results, key=lambda x: x['similarity'], reverse=True)

        return jsonify({'matches': results[:5]})  # Return top 5 matches
    
    return jsonify({'error': 'Invalid file format'}), 400
