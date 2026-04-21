from fastapi import FastAPI, Request
from google.cloud import storage
import os
import base64
import json
import pandas as pd

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Cloud Run started working!"}
 
@app.post("/")
async def receive_pubsub(request: Request):

    print(" Request is recieved ")    

    envelope = await request.json()
    print("message: ", envelope)


    pubsub_message = envelope["message"]
    print("pub/sub message:", pubsub_message)
    decoded_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
    event_data = json.loads(decoded_data)

    bucket_name = event_data["bucket"]
    file_name = event_data["name"]

    print("Bucket Name: ", bucket_name)
    print("File Name: ", file_name)

    if not file_name.startswith("raw/"):
        print(f"Not in folder - {file_name}" )
        return {"status": "not processed"}

    if file_name.endswith(".parquet"):
        print (f"skipping: not a json file - {file_name}")
        return {"status": "not processed"}

    if not file_name.endswith(".json"):
        print(f"not a json file-{file_name} ")
        return {"status": "not processed"}

    print(f"Processing json file: {file_name}")

        
    bucket = storage.Client().bucket(bucket_name)
    blob = bucket.blob(file_name)

    file_content= blob.download_as_bytes()
    
    json_content = json.loads(file_content)

    print ("file content: ", json_content)
    # print(" processing completed")
    # return {"status": "processed"}

    df = pd.DataFrame([json_content])
    print("dataframe created")
    parquet_file_name = file_name.replace("raw/", "converted/")
    parquet_file_name = parquet_file_name.replace(".json", ".parquet")
    local_path = f"/tmp/{parquet_file_name}"
    df.to_parquet(local_path, index=False)
    print("parquet file created")
    
    parquet_blob = bucket.blob(parquet_file_name)
    parquet_blob.upload_from_filename(local_path)

    if os.path.exists(local_path):
        os.remove(local_path)


    print("parquet file uploaded to GCS")

    return {"status": "processed"}






