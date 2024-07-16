from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/log_data', methods=['POST'])
def log_data():
    data = request.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"smoke_data_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f)
    
    return jsonify({"status": "success", "filename": filename})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)