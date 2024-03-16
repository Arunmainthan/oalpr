import requests
from flask import Flask, request, jsonify
import logging
from openalpr import Alpr

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenALPR
lpr = Alpr("eu", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
lpr.set_default_region("pt")
if not lpr.is_loaded():
    logging.error("Error loading OpenALPR")
    sys.exit(1)

# Define the route for plate recognition
@app.route('/recognize', methods=['POST'])
def recognize_plate():
    data = request.get_json()
    if 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400
    image_url = data['url']
    
    # Fetch the image from the URL
    response = requests.get(image_url)
    if response.status_code != 200:
        return jsonify({"error": "Image could not be retrieved"}), 400
    
    # Save the image to a temporary file
    temp_image_path = "/tmp/plate.jpg"
    with open(temp_image_path, 'wb') as temp_image:
        temp_image.write(response.content)

    # Perform recognition
    lpr_results = lpr.recognize_file(temp_image_path)
    recognized_plates = [result['plate'] for result in lpr_results['results']]

    # Clean up the temporary file
    os.remove(temp_image_path)

    # Return the recognition results
    if recognized_plates:
        return jsonify({"plates": recognized_plates})
    else:
        return jsonify({"error": "No plates recognized"})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
