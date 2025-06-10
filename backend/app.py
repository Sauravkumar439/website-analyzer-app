from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import analyze_website

app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": "http://localhost:3000"}})  # Allow only frontend origin

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    result = analyze_website(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
