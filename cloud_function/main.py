import functions_framework # type: ignore
from google.cloud import storage, bigquery
from googleapiclient.discovery import build # type: ignore
from google.auth import default # type: ignore
from datetime import datetime, UTC
import csv
import io

# Define variables for Cloud Functions
PROJECT_ID = "tv-performance"
DATASET_ID = "tv_analytics"
TABLE_ID = "ratings"
BUCKET_NAME = "tv-performance-bucket"

SPREADSHEET_ID = "1Sp3q8og7ceZ702NXqG3M5MxRDghpPEh_3WGW5d88RTM"   
SHEET_RANGE = "tv_data_performance"  

DESTINATION_LATEST = "tv-performance/latest/data.csv"

# Extract data from Google Sheets
def get_sheet_data():

    # Obtain application default credentials with read-only access
    creds, _ = default(scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])

    # Obtain application default credentials with read-only access
    service = build("sheets", "v4", credentials=creds)

    # Obtain application default credentials with read-only access
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE
    ).execute()

    return result.get("values", [])


# Converts sheet rows to CSV format
def rows_to_csv_bytes(rows):
    buf = io.StringIO()
    writer = csv.writer(buf)

    # Write all rows to the in-memory CSV buffer
    writer.writerows(rows)

    # Convert string content to bytes for upload
    return buf.getvalue().encode("utf-8")


def upload_to_gcs(bucket_name, data_bytes, destination_blob):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)

    # Upload content as a CSV file
    blob.upload_from_string(data_bytes, content_type="text/csv")
    print(f"Uploaded → gs://{bucket_name}/{destination_blob}")


def load_to_bigquery(gcs_uri):
    client = bigquery.Client(project=PROJECT_ID)

    # Fully qualified table name
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    #Config BigQuery load jon
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_TRUNCATE",
    )

    # Start job
    job = client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)

    # Wait for job completion
    job.result()

    print(f"Loaded into BigQuery: {table_ref}")


@functions_framework.http
def sync_pipeline(request):

    # Create a partition-style folder using today's UTC date
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    destination_dated = f"tv-performance/dt={today}/data.csv"

    # Extract data from Google Sheets
    rows = get_sheet_data()

    # Convert rows to CSV bytes
    csv_bytes = rows_to_csv_bytes(rows)

    # Upload latest version (always overwritten)
    upload_to_gcs(BUCKET_NAME, csv_bytes, DESTINATION_LATEST)

    # Upload dated archive version 
    upload_to_gcs(BUCKET_NAME, csv_bytes, destination_dated)

    # Load archived file into BigQuery
    gcs_uri = f"gs://{BUCKET_NAME}/{destination_dated}"
    load_to_bigquery(gcs_uri)

    return "OK", 200