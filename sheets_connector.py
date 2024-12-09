from flask import Flask, jsonify, request
from flask_cors import CORS
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Google Sheets API configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
SPREADSHEET_ID = os.getenv('GOOGLE_SHEET_ID')
RANGE_NAME = os.getenv('SPREADSHEET_RANGE')

# Authenticate with Google Sheets API
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)


@app.route('/api/sheet-data', methods=['GET'])
def get_sheet_data():
    try:
        # Connect to Google Sheets API
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        rows = result.get('values', [])

        # Convert rows into a list of dictionaries
        if rows:
            headers = rows[0]  # Use the first row as headers
            data = [dict(zip(headers, row)) for row in rows[1:]]
        else:
            data = []

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
