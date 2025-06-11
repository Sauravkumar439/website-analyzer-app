# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import analyze_website  # Ensure this function is defined in analyzer.py

app = Flask(__name__)

# Allow requests from your frontend (Netlify) and local development
CORS(app, resources={r"/analyze": {"origins": [
    "http://localhost:3000",
    "https://website-analyzer-app.netlify.app"
]}})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        result = analyze_website(url)
        return jsonify(result)
    except Exception as e:
        print("Error during analysis:", e)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Railway sets the PORT environment variable dynamically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
