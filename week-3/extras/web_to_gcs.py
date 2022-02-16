import io
import os
import requests
import pandas as pd
import pyarrow
from google.cloud import storage

"""
Pre-reqs: 
1. `pip install pandas pyarrow google-cloud-storage`
2. Set GOOGLE_APPLICATION_CREDENTIALS to your project/service-account key
3. Set GCP_GCS_BUCKET as your bucket or change default value of BUCKET
"""

# services = ['fhv','green','yellow']
init_url = "https://nyc-tlc.s3.amazonaws.com/trip+data/"
BUCKET = os.environ.get("GCP_GCS_BUCKET", "dtc_data_lake_basic-strata-340105")


def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    """
    # # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # # (Ref: https://github.com/googleapis/python-storage/issues/74)
    # storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    # storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    client = storage.Client()
    bucket = client.bucket(bucket)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


table_schema = pyarrow.schema(
    [
        ("VendorID", pyarrow.string()),
        ("lpep_pickup_datetime", pyarrow.timestamp("s")),
        ("lpep_dropoff_datetime", pyarrow.timestamp("s")),
        ("store_and_fwd_flag", pyarrow.string()),
        ("RatecodeID", pyarrow.int64()),
        ("PULocationID", pyarrow.int64()),
        ("DOLocationID", pyarrow.int64()),
        ("passenger_count", pyarrow.int64()),
        ("trip_distance", pyarrow.float64()),
        ("fare_amount", pyarrow.float64()),
        ("extra", pyarrow.float64()),
        ("mta_tax", pyarrow.float64()),
        ("tip_amount", pyarrow.float64()),
        ("tolls_amount", pyarrow.float64()),
        ("ehail_fee", pyarrow.float64()),
        ("improvement_surcharge", pyarrow.float64()),
        ("total_amount", pyarrow.float64()),
        ("payment_type", pyarrow.int64()),
        ("trip_type", pyarrow.int64()),
        ("congestion_surcharge", pyarrow.float64()),
    ]
)


def web_to_gcs(year, service):
    for i in range(13):
        month = "0" + str(i + 1)
        month = month[-2:]
        file_name = service + "_tripdata_" + year + "-" + month + ".csv"
        request_url = init_url + file_name
        r = requests.get(request_url)
        pd.DataFrame(io.StringIO(r.text)).to_csv(file_name)
        print(f"Local: {file_name}")
        df = pd.read_csv(file_name)
        print(df.head())
        break
        # df = df.drop("ehail_fee", axis=0)
        # file_name = file_name.replace(".csv", ".parquet")
        # df.to_parquet(file_name, engine="pyarrow")
        # print(f"CSV: {file_name}")
        # upload_to_gcs(BUCKET, f"{service}_parquet/{file_name}", file_name)
        # print(f"GCS: {service}/{file_name}")


web_to_gcs("2019", "green")
web_to_gcs("2020", "green")
# web_to_gcs("2019", "yellow")
# web_to_gcs("2020", "yellow")