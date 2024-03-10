import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app, supports_credentials=True)  # Enable CORS with credentials support

@app.route('/get_booking_details', methods=['POST'])
def get_booking_details():
    # Get JSON data from the request
    request_data = request.json

    # Extract data from JSON
    therapist_id = request_data.get('therapist_id')
    loc_id = request_data.get('loc_id')
    service_id = request_data.get('service_id')
    auth_token = request_data.get('auth_token')
    base_url = request_data.get('base_url')

    # Check if all required fields are present
    if not all([therapist_id, loc_id, service_id, auth_token, base_url]):
        return jsonify({'error': 'Missing required fields in JSON data'}), 400

    # URL of the slots page
    url = f'{base_url}?therapiest_id={therapist_id}&location={loc_id}&therapy_for_id={service_id}'

    # Extract User-Agent from the incoming request headers
    user_agent = request.headers.get('User-Agent')

    cookies = request.cookies

    # Define the headers for the outgoing request
    headers = {
        'User-Agent': user_agent
    }

    # Create a session to handle cookies
    with requests.Session() as session:
        # Send a GET request to the slots page with the User-Agent header
        response = session.get(url, headers=headers)

        # Check if the request was successful
        if response.ok:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the div with an ID containing the pattern 'bookly-form-'
            pattern = re.compile(r'bookly-form-\w+')
            bookly_form = soup.find('div', id=pattern)

            bookly_form_id = bookly_form['id'].split('-')[-1] if bookly_form else None

            # Get PHPSESSID cookie value
            phpsessid_cookie = session.cookies.get('PHPSESSID')

            # Find the <script> tag with ID "bookly-globals-js-extra"
            script_tag = soup.find('script', id='bookly-globals-js-extra')

            script_content = script_tag.string if script_tag else ''
            csrf_token_match = re.search(r'(?<=csrf_token":")\w+', script_content)
            csrf_token = csrf_token_match.group(0) if csrf_token_match else None

            # Prepare response
            response_data = {
                'bookly_form_id': bookly_form_id,
                'phpsessid_cookie': phpsessid_cookie,
                'csrf_token': csrf_token,
                'url': url,
                'headers': headers,
                'cookies': cookies
            }

            return jsonify(response_data), 200
        else:
            return jsonify(
                {'error': f'Failed to fetch page. Status code: {response.status_code}'}), response.status_code


@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
