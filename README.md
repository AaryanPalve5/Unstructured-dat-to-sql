# File to SQL API Documentation

This documentation outlines the structure and functionality of the `File to SQL` application, designed to handle file uploads, process them into structured tables, and store them in an SQLite database.

---

## Overview
The `File to SQL` API supports uploading various file types, converting them into structured tables, and storing them in an SQLite database. It also provides functionality to retrieve the schema of a specific table.

---

## Tech Stack
- **Backend Framework**: FastAPI
- **Frontend Templates**: Jinja2
- **Database**: SQLite
- **Libraries**: Pandas, OpenPyXL

---

## Running the Application

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn pandas openpyxl jinja2
   ```

2. **Run the Application**:
   ```bash
   uvicorn trial2:app --reload
   ```

3. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

---

## API Endpoints

### 1. **Root Endpoint**
- **URL**: `/`
- **Method**: `GET`
- **Response**: HTML page with a file upload form.
- **Description**: Serves the frontend for file uploads.

### 2. **Upload Files**
- **URL**: `/upload`
- **Method**: `POST`
- **Parameters**:
  - `files`: A list of files to upload (supports `.csv`, `.xls`, `.xlsx`, `.json`, `.xml`, `.parquet`, `.txt`).
- **Response**:
  ```json
  {
      "results": [
          {"file": "filename.csv", "message": "File successfully processed and saved to table 'filename'."},
          {"file": "filename.json", "message": "Error processing file: ..."}
      ]
  }
  ```
- **Description**: Processes uploaded files and saves their contents into corresponding SQLite tables.

### 3. **Get Table Schema**
- **URL**: `/schema/{table_name}`
- **Method**: `GET`
- **Parameters**:
  - `table_name`: Name of the table whose schema you want to retrieve.
- **Response**:
  ```json
  {
      "table": "table_name",
      "columns": [
          {"name": "column1", "type": "TEXT"},
          {"name": "column2", "type": "INTEGER"}
      ]
  }
  ```
- **Description**: Retrieves the schema of the specified SQLite table.

---

## File Processing Logic

### Supported File Types
- **CSV**: Parsed using `pandas.read_csv`.
- **Excel (.xls, .xlsx)**: Parsed using `pandas.read_excel` with `openpyxl` engine.
- **JSON**: Parsed using `json.load` and normalized with `pandas.json_normalize`.
- **XML**: Parsed using `pandas.read_xml`.
- **Parquet**: Parsed using `pandas.read_parquet`.
- **Text (.txt)**: Assumes tab-delimited format, parsed using `pandas.read_csv`.

### Processing Steps
1. Upload the file.
2. Save it to the `uploads/` directory.
3. Parse the file into a Pandas DataFrame based on its extension.
4. Save the DataFrame to SQLite using the file name (without extension) as the table name.

---

## Project Directory Structure
```
project-root/
|— trial2.py                # Main application file
|— templates/
   |— index.html           # Frontend template for file uploads
|— uploads/              # Directory for storing uploaded files
|— files2.db              # SQLite database file
```

---

## Frontend Template
**File**: `templates/index.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File to SQL</title>
</head>
<body>
    <h1>Upload Files to SQL</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <label for="files">Upload files:</label>
        <input type="file" id="files" name="files" multiple required>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
```

---

## Notes for Developers
- **Backend Developers**:
  - Extend the `/upload` endpoint to support additional file formats if needed.
  - Add error handling for edge cases, such as malformed files.
  - Optimize database write operations for large files.

- **Frontend Developers**:
  - Enhance the UI/UX of the `index.html` template.
  - Implement better error handling and feedback for users.
  - Consider adding a dashboard to display uploaded tables and their schemas.

---

## Example Requests

### Upload Files
**Request**:
```bash
curl -X POST "http://127.0.0.1:8000/upload" \
     -F "files=@test.csv" \
     -F "files=@test.json"
```

**Response**:
```json
{
    "results": [
        {"file": "test.csv", "message": "File 'test.csv' successfully processed and saved to table 'test'."},
        {"file": "test.json", "message": "File 'test.json' successfully processed and saved to table 'test'."}
    ]
}
```

### Retrieve Table Schema
**Request**:
```bash
curl -X GET "http://127.0.0.1:8000/schema/test"
```

**Response**:
```json
{
    "table": "test",
    "columns": [
        {"name": "column1", "type": "TEXT"},
        {"name": "column2", "type": "INTEGER"}
    ]
}
```

