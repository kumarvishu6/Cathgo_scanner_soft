from flask import Blueprint, render_template, jsonify
import random

dashboard_bp = Blueprint('dashboard', __name__)

# Mock data for dashboard
@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('index.html')

# API Route for fetching analytics stats
@dashboard_bp.route('/api/stats')
def get_stats():
    stats_data = {
        "total_scans": random.randint(50, 500),  # Replace with actual DB values
        "recent_uploads": random.randint(5, 50),
        "credits_remaining": random.randint(100, 1000),
        "top_topics": ["AI", "Blockchain", "Cybersecurity"],  # Replace with DB values
        "top_users": ["user1", "user2", "user3"]
    }
    return jsonify(stats_data)
