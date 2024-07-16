# server.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/hemp_smoke_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
limiter = Limiter(app, key_func=get_remote_address)

# Set up logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/hemp_smoke_server.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Define database models
class Session(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    start_time = db.Column(db.DateTime)
    duration = db.Column(db.Float)
    peak_opacity = db.Column(db.Float)
    opacity_change_rate = db.Column(db.Float)
    significant_changes = db.Column(db.Integer)
    ambient_light_level = db.Column(db.Float)
    clearing_time = db.Column(db.Float)

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), db.ForeignKey('session.id'))
    timestamp = db.Column(db.DateTime)
    value = db.Column(db.Float)

@app.route('/log_data', methods=['POST'])
@limiter.limit("10/minute")
def log_data():
    try:
        data = request.json
        log_data = data.get('log_data', [])
        
        for entry in log_data:
            if 'duration' in entry:  # This is a session summary
                session = Session(
                    id=entry['session_id'],
                    start_time=entry['timestamp'],
                    duration=entry['duration'],
                    peak_opacity=entry['peak_opacity'],
                    opacity_change_rate=entry['opacity_change_rate'],
                    significant_changes=entry['significant_changes'],
                    ambient_light_level=entry['ambient_light_level'],
                    clearing_time=entry['clearing_time']
                )
                db.session.add(session)
            else:  # This is a data point
                data_point = DataPoint(
                    session_id=entry['session_id'],
                    timestamp=entry['timestamp'],
                    value=entry['value']
                )
                db.session.add(data_point)
        
        db.session.commit()
        app.logger.info(f"Logged data for session {data.get('session_id')}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        app.logger.error(f"Error logging data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)