from flask import Flask, jsonify, request
from flask_cors import CORS
import re
import random
import requests
import json
from bs4 import BeautifulSoup

app = Flask(__name__)

CORS(app)

user_agents = [
    # Windows User-Agents
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',

    # Mac User-Agents
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',

    # Linux User-Agents
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0',

    # Android User-Agents
    'Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.101 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
]


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

    # Randomly select a User-Agent header
    user_agent = random.choice(user_agents)

    # Define the User-Agent header using the randomly selected User-Agent string
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
                'headers': headers
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
