import os
import io
import pandas as pd
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", None)
S3_BUCKET = os.getenv("S3_BUCKET", "rev-labs-weather-reports")
S3_REGION = os.getenv("AWS_REGION", "eu-west-2")
S3_PUBLIC_URL_FMT = os.getenv("S3_PUBLIC_URL_FMT", None)

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)


def upload_csv(df: pd.DataFrame, key: str) -> str:
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)

    session_kwargs = {}
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        session_kwargs.update({
            'aws_access_key_id': AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': AWS_SECRET_ACCESS_KEY
        })
    
    session = boto3.session.Session(**session_kwargs)
    
    client_kwargs = {
        "service_name": "s3",
        "region_name": S3_REGION,
        "config": Config(s3={"addressing_style": "virtual"})
    }
    
    if AWS_ENDPOINT:
        client_kwargs["endpoint_url"] = AWS_ENDPOINT
    
    s3 = session.client(**client_kwargs)
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
    except Exception as e:
        if AWS_ENDPOINT is not None:
            try:
                s3.create_bucket(Bucket=S3_BUCKET)
            except Exception as create_error:
                print(f"Warning: Could not create bucket {S3_BUCKET}: {create_error}")
        else:
            print(f"Assuming bucket {S3_BUCKET} exists in AWS S3")

    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=buf.getvalue(), ContentType="text/csv")

    if S3_PUBLIC_URL_FMT:
        return S3_PUBLIC_URL_FMT.format(bucket=S3_BUCKET, key=key, region=S3_REGION)
    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"