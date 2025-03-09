import os
from flask import Flask, request, jsonify, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, current_user
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
import difflib  # ✅ For basic text similarity

# ✅ Initialize Extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # ✅ Configuration
    app.config['SECRET_KEY'] = '832107'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['UPLOAD_FOLDER'] = 'uploads'

    # ✅ Ensure Uploads Folder Exists
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    # ✅ Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  
    jwt.init_app(app)
    CORS(app)  

    # ✅ Import models AFTER initializing db to avoid circular import
    from models import User, Document  

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ Import and register blueprints
    from routes.auth_routes import auth_blueprint 
    from routes.scan_routes import scan_bp
    from routes.credit_routes import credit_blueprint
    from routes.document_routes import document_bp
    from routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(credit_blueprint)
    app.register_blueprint(scan_bp)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # ✅ Home Route
    @app.route("/")
    def home():
        return "Welcome to the Document Scanner System!"

    # ✅ Serve Upload Page
    @app.route("/upload", methods=["GET"])
    @login_required
    def upload_page():
        return render_template("upload.html")

    # ✅ API Endpoint: Upload & Scan Document
    @app.route("/api/scan", methods=["POST"])
    @jwt_required()
    def scan_document():
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        if "document" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["document"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # ✅ Read the uploaded file
        with open(file_path, "r", encoding="utf-8") as f:
            uploaded_text = f.read()

        # ✅ Fetch all stored documents for matching
        stored_documents = Document.query.all()
        match_results = []

        for doc in stored_documents:
            similarity = text_similarity(uploaded_text, doc.content)
            match_results.append({"document_name": doc.filename, "similarity_score": similarity})

        # ✅ Sort by highest similarity
        match_results = sorted(match_results, key=lambda x: x["similarity_score"], reverse=True)

        return jsonify({"matches": match_results})

    def text_similarity(text1, text2):
        """Basic text similarity using SequenceMatcher"""
        return round(difflib.SequenceMatcher(None, text1, text2).ratio() * 100, 2)

    return app

# ✅ Create the application instance and expose it for imports
app = create_app()

# ✅ Ensure DB tables are created only when running the app (avoids issues with migrations)
with app.app_context():
    db.create_all()

# ✅ Run the app
if __name__ == '__main__':
    app.run(debug=True)
