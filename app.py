from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import sqlite3
from pathlib import Path
import json

app = FastAPI()

# Set up Jinja2 templates for frontend
templates = Jinja2Templates(directory="templates")

# SQLite database file
DATABASE_FILE = "files2.db"

# Helper to load data and write to SQLite
def process_file_to_sql(file_path: str, file_extension: str):
    try:
        # Load the file into a DataFrame based on the extension
        if file_extension == ".csv":
            df = pd.read_csv(file_path)
        elif file_extension in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path, engine="openpyxl")  # Specify engine explicitly
        elif file_extension == ".json":
            with open(file_path, "r") as f:
                raw_data = json.load(f)
            # Normalize nested JSON if needed
            df = pd.json_normalize(raw_data)
        elif file_extension == ".xml":
            df = pd.read_xml(file_path)
        elif file_extension == ".parquet":
            df = pd.read_parquet(file_path)
        elif file_extension == ".txt":
            df = pd.read_csv(file_path, delimiter="\t")  # Assuming tab-delimited
        else:
            return f"Unsupported file format: {file_extension}"

        if df.empty:
            return f"File '{file_path}' is empty or could not be parsed."

        # Use the file name (without extension) as the table name
        table_name = Path(file_path).stem

        # Write the DataFrame to SQLite
        with sqlite3.connect(DATABASE_FILE) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)

        return f"File '{file_path}' successfully processed and saved to table '{table_name}'."
    except Exception as e:
        return f"Error processing file '{file_path}': {str(e)}"

# Endpoint to serve the frontend
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to handle multiple file uploads
@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    results = []
    try:
        upload_dir = Path("uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            file_location = upload_dir / file.filename
            with open(file_location, "wb") as f:
                f.write(await file.read())

            # Process the file based on its extension
            file_extension = file_location.suffix.lower()
            result = process_file_to_sql(str(file_location), file_extension)
            results.append({"file": file.filename, "message": result})

        return {"results": results}
    except Exception as e:
        return {"error": f"Failed to upload and process files: {str(e)}"}

# Endpoint to get the schema of a specific table
@app.get("/schema/{table_name}")
def get_table_schema(table_name: str):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema_info = cursor.fetchall()

        # Format the response
        schema = [
            {
                "column_id": row[0],
                "name": row[1],
                "type": row[2],
                "not_null": bool(row[3]),
                "default_value": row[4],
                "primary_key": bool(row[5]),
            }
            for row in schema_info
        ]

        if not schema:
            return {"error": f"Table '{table_name}' does not exist or has no schema."}

        return {"table": table_name, "schema": schema}
    except Exception as e:
        return {"error": f"Failed to retrieve schema for table '{table_name}': {str(e)}"}

# Frontend template: templates/index.html
index_html = """<!DOCTYPE html>
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
</html>"""

# Write the template to a file
Path("templates").mkdir(parents=True, exist_ok=True)
with open("templates/index.html", "w") as f:
    f.write(index_html)

# Ensure the SQLite database file exists
if not Path(DATABASE_FILE).exists():
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS example (id INTEGER PRIMARY KEY)")
