from flask import Flask, request, render_template, jsonify
import pandas as pd
import sqlite3
from pathlib import Path
import json

app = Flask(__name__)

# SQLite database file
DATABASE_FILE = "files2.db"

# Helper to load data and write to SQLite
def process_file_to_sql(file_path: str, file_extension: str):
    try:
        # Load the file into a DataFrame based on the extension
        if file_extension == ".csv":
            df = pd.read_csv(file_path)
        elif file_extension in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path, engine="openpyxl")
        elif file_extension == ".json":
            with open(file_path, "r") as f:
                raw_data = json.load(f)
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

# Route to serve the frontend
@app.route("/")
def index():
    return render_template("index.html")

# Route to handle file uploads
@app.route("/upload", methods=["POST"])
def upload_files():
    results = []
    try:
        upload_dir = Path("uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        files = request.files.getlist("files")
        for file in files:
            file_location = upload_dir / file.filename
            file.save(file_location)

            # Process the file based on its extension
            file_extension = file_location.suffix.lower()
            result = process_file_to_sql(str(file_location), file_extension)
            results.append({"file": file.filename, "message": result})

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": f"Failed to upload and process files: {str(e)}"})

# Route to get the schema of a specific table
@app.route("/schema/<table_name>")
def get_table_schema(table_name):
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
            return jsonify({"error": f"Table '{table_name}' does not exist or has no schema."})

        return jsonify({"table": table_name, "schema": schema})
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve schema for table '{table_name}': {str(e)}"})

# Ensure the SQLite database file exists
if not Path(DATABASE_FILE).exists():
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS example (id INTEGER PRIMARY KEY)")

if __name__ == "__main__":
    # Create the templates folder and index.html if not present
    Path("templates").mkdir(parents=True, exist_ok=True)
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
    with open("templates/index.html", "w") as f:
        f.write(index_html)

    app.run(debug=True)
