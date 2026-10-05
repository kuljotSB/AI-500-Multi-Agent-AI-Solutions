import os

from flask import Flask, jsonify, Response

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os

# ------------------------------------------
# Configuration
# ------------------------------------------

STORAGE_ACCOUNT_NAME = os.environ.get("STORAGE_ACCOUNT_NAME")
CONTAINER_NAME = os.environ.get("STORAGE_CONTAINER_NAME")

ACCOUNT_URL = (
    f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
)

# ------------------------------------------
# Managed Identity Authentication
# ------------------------------------------

credential = DefaultAzureCredential()

blob_service_client = BlobServiceClient(
    account_url=ACCOUNT_URL,
    credential=credential
)

container_client = blob_service_client.get_container_client(
    CONTAINER_NAME
)

# ------------------------------------------
# Flask App
# ------------------------------------------

app = Flask(__name__)

# ------------------------------------------
# List all blobs
# ------------------------------------------

@app.get("/blobs")
def list_blobs():

    blobs = []

    for blob in container_client.list_blobs():

        blobs.append({
            "name": blob.name,
            "size": blob.size,
            "last_modified": str(blob.last_modified)
        })

    return jsonify(blobs)


# ------------------------------------------
# Read blob contents
# ------------------------------------------

@app.get("/blob/<path:blob_name>")
def read_blob(blob_name):

    blob_client = container_client.get_blob_client(blob_name)

    data = blob_client.download_blob().readall()

    return Response(
        data,
        mimetype="text/plain"
    )


# ------------------------------------------
# Health Endpoint
# ------------------------------------------

@app.get("/")
def home():

    return {
        "authentication": "Managed Identity",
        "storage_account": STORAGE_ACCOUNT_NAME,
        "container": CONTAINER_NAME
    }


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )