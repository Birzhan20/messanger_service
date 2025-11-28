import io
import os
import aioboto3
from dotenv import load_dotenv

load_dotenv()

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
URL = os.getenv("S3_URL")
S3_URL = f"https://{URL}"

async def upload_to_s3(file_obj: bytes, file_name: str):
    session = aioboto3.Session()
    async with session.client(
        service_name="s3",
        endpoint_url=S3_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name="auto",
    ) as s3:
        file_obj_io = io.BytesIO(file_obj)
        await s3.upload_fileobj(file_obj_io, S3_BUCKET, file_name)
    public_url = f"{S3_URL}/{S3_BUCKET}/{file_name}"
    return public_url

async def delete_from_s3(file_name: str):
    session = aioboto3.Session()
    async with session.client(
        service_name="s3",
        endpoint_url=S3_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name="auto",
    ) as s3:
        await s3.delete_object(Bucket=S3_BUCKET, Key=file_name)
