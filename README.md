### Documentation for File-to-SQL Mapping Application
![](ss.jpeg)

#### Overview
This application allows users to upload various file formats (e.g., CSV, Excel, JSON, XML, Parquet) and store the data in an SQLite database. Additionally, if the data includes a `location` column, the app geocodes these locations to add latitude and longitude, enabling interactive map visualizations.

---

### Features
1. **File Upload and Processing**:
   - Supports file formats: `.csv`, `.xls`, `.xlsx`, `.json`, `.xml`, `.parquet`, `.txt` (tab-delimited).
   - Converts files to structured tables and saves them in an SQLite database.
   - Handles multiple file uploads at once.

2. **Geocoding**:
   - If a `location` column exists, it is geocoded to add `latitude` and `longitude` columns.
   - Uses the `geopy` library for geocoding.

3. **Map Visualization**:
   - Generates an interactive map for tables containing geocoded data.
   - Displays markers for each geocoded location.

4. **Frontend**:
   - Simple HTML-based interface for file uploads.
   - Map rendering via a dynamically generated HTML template.

---

### API Endpoints

#### 1. `GET /`
**Description**: Serves the main HTML interface for file uploads.  
**Response**: HTML page with a file upload form.

---

#### 2. `POST /upload`
**Description**: Handles file uploads, processes files, and stores data in the SQLite database.  
**Request**:
- `files` (multipart/form-data): One or more files to upload.  

**Response**:
- JSON response containing the status of each file upload:
  ```json
  {
      "results": [
          {"file": "example.csv", "message": "File 'example.csv' successfully processed and saved to table 'example'."},
          {"file": "data.xlsx", "message": "File 'data.xlsx' successfully processed and saved to table 'data'."}
      ]
  }
  ```

---

#### 3. `GET /map/<table_name>`
**Description**: Renders an interactive map for a specific table containing `latitude` and `longitude` columns.  
**Path Parameter**:
- `table_name`: The name of the table to visualize.

**Response**:
- HTML page with an interactive map.  
- Error message if the table does not contain geocoded data.

---

### File Processing Workflow
1. **File Parsing**:
   - Reads files into Pandas DataFrames based on the file extension.
   - Handles empty or unsupported files gracefully.

2. **Geocoding**:
   - Checks for a `location` column in the uploaded data.
   - Uses the `geopy` library to fetch latitude and longitude for each location.
   - Adds `latitude` and `longitude` columns to the DataFrame.

3. **Database Storage**:
   - Saves the DataFrame as a table in the SQLite database (`files2.db`).
   - Overwrites existing tables with the same name.

---

### Interactive Map
- Uses `folium` to generate a map centered on the average latitude and longitude of the geocoded data.
- Adds markers for each location with a popup showing the location name (if available).

---

### Deployment
1. **Dependencies**:
   Install the required Python libraries using:
   ```bash
   pip install flask pandas sqlite3 geopy folium openpyxl
   ```

2. **Database**:
   - SQLite database is created automatically (`files2.db`).

3. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will be accessible at `http://127.0.0.1:5000`.

---

### File Structure
```
.
├── app.py                # Main application script
├── templates/
│   ├── index.html        # HTML template for file upload
│   └── map.html          # HTML template for interactive map
├── uploads/              # Directory for uploaded files
└── files2.db             # SQLite database (generated at runtime)
```

---

### Example Usage
1. Navigate to the file upload page at `http://127.0.0.1:5000`.
2. Upload one or more files.
3. View the processing results in the JSON response.
4. If a file contains a `location` column, access the map at `http://127.0.0.1:5000/map/<table_name>`.

---

### Notes
- Ensure a stable internet connection for geocoding with `geopy`.
- Large datasets may require additional time for geocoding and processing.


### Google sheets connector

1. Install Dependencies
2. 
Make sure you have Python installed. You will need to install the necessary dependencies by running:

pip install flask flask-cors google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv openai

2. Set Up Google Sheets API

To authenticate with Google Sheets and fetch data, follow these steps:

Enable the Google Sheets API: Go to the Google Cloud Console, create a project, and enable the Google Sheets API.

Create a Service Account:

In the Google Cloud Console, navigate to IAM & Admin > Service Accounts.

Create a new service account with the Editor role.

Download the JSON key file.

Share Your Google Sheet: Share the Google Sheet with the service account email (found in the JSON key file).

3. Set Up Environment Variables
Create a .env file in the project directory to store sensitive information:

GOOGLE_SERVICE_ACCOUNT_FILE=path/to/your/service_account_key.json

GOOGLE_SHEET_ID=your-google-sheet-id

SPREADSHEET_RANGE=your-range (e.g., 'Sheet1!A1:C10')

Replace path/to/your/service_account_key.json with the path to the downloaded service account key file.

Replace your-google-sheet-id with the actual ID of the Google Sheet (from the URL).

Replace your-range with the range of cells you want to fetch data from (e.g., Sheet1!A1:C10).

4. Running the Flask App
In your terminal, navigate to the project directory where your app.py file is located and run the following command:

python app.py
This will start the Flask server on http://127.0.0.1:5000/.

5. Test the API
Open your browser and navigate to:

http://127.0.0.1:5000/api/sheet-data
This should return the data from your Google Sheet in JSON format.

