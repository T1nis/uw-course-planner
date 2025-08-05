from flask import Flask, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/courses')
def get_courses():
    # Build absolute path to courses directory
    base_dir = os.path.dirname(__file__)
    courses_dir = os.path.abspath(os.path.join(base_dir, 'scripts/c-data/courses'))
    courses = []
    if not os.path.exists(courses_dir):
        return jsonify([])  # Return empty if not found
    for filename in os.listdir(courses_dir):
        if filename.endswith('.json'):
            with open(os.path.join(courses_dir, filename), 'r', encoding='utf-8') as f:
                courses.append(json.load(f))
    return jsonify(courses)

if __name__ == "__main__":
    app.run(port=5000)