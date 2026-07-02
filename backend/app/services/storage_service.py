import os
import logging
from typing import Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket_name = settings.MINIO_BUCKET_NAME
        
        # Local fallback directory
        self.fallback_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static_storage")
        os.makedirs(self.fallback_dir, exist_ok=True)
        
        self.use_fallback = False
        self.s3_client = None
        
        # Initialize S3 client
        try:
            # Config with short timeouts so it falls back quickly if MinIO is not running
            config = Config(connect_timeout=2, read_timeout=2, retries={'max_attempts': 1})
            
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=config,
                region_name="us-east-1"
            )
            
            # Try to verify/create bucket
            self._ensure_bucket_exists()
        except Exception as e:
            logger.warning(f"S3 connection failed ({str(e)}). Falling back to local filesystem storage.")
            self.use_fallback = True

    def _ensure_bucket_exists(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404' or error_code == 'NoSuchBucket':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"S3 Bucket '{self.bucket_name}' created successfully.")
                except Exception as create_err:
                    logger.error(f"Could not create S3 bucket: {str(create_err)}")
                    self.use_fallback = True
            else:
                logger.error(f"S3 head_bucket error: {str(e)}")
                self.use_fallback = True

    async def upload_file(self, file_data: bytes, file_name: str, content_type: str = "audio/mpeg") -> str:
        """Uploads a file and returns its storage locator key (file_name or local path)."""
        if self.use_fallback:
            local_path = os.path.join(self.fallback_dir, file_name)
            with open(local_path, "wb") as f:
                f.write(file_data)
            logger.info(f"Saved file locally: {local_path}")
            return f"local://{file_name}"
            
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_data,
                ContentType=content_type
            )
            logger.info(f"Uploaded file to S3: {file_name}")
            return file_name
        except Exception as e:
            logger.error(f"S3 upload failed for {file_name}: {str(e)}. Attempting local save.")
            # Emergency local save
            local_path = os.path.join(self.fallback_dir, file_name)
            with open(local_path, "wb") as f:
                f.write(file_data)
            return f"local://{file_name}"

    async def get_streaming_url(self, storage_key: str, expires_in: int = 3600) -> str:
        """Generates a temporary signed URL for S3 or a local server path for local files."""
        if not storage_key:
            return ""
            
        if storage_key.startswith("local://"):
            file_name = storage_key.replace("local://", "")
            # Return path mapped to a local server route
            return f"/api/music/file/{file_name}"
            
        if self.use_fallback or not self.s3_client:
            # If storage_key isn't prefix but we switched to fallback, check if local file exists
            return f"/api/music/file/{storage_key}"
            
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': storage_key
                },
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            # Fallback local URL
            return f"/api/music/file/{storage_key}"

storage_service = StorageService()
