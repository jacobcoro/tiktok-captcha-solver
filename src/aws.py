import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

from logger import get_logger

load_dotenv()
logger = get_logger(__name__)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
AWS_BUCKET = os.getenv("AWS_BUCKET")

boto3.setup_default_session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)


class ScreenshotStorage:
    def __init__(self, bucket_name: str = AWS_BUCKET, region_name: str = AWS_DEFAULT_REGION):
        """
        Initialize AWS S3 client

        Args:
            bucket_name: Name of the S3 bucket
            region_name: AWS region name (default: us-east-1)
        """
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.bucket_name = bucket_name
        self.region_name = region_name

    def save_screenshot(self, screenshot_bytes: bytes, save_as_name: str) -> Optional[str]:
        """
        Save screenshot to local storage and upload to S3

        Args:
            screenshot_bytes: The screenshot data as bytes
            save_as_name: Name to save the file as

        Returns:
            str: URL of the uploaded file in S3, or None if upload fails
        """
        try:
            # Create path similar to PHP version
            path = f"tiktokbot-screenshots/{
                datetime.now().strftime('%Y-%m-%d')}/"
            filename = f"{save_as_name}.png"
            full_path = path + filename

            # Upload directly to S3 from memory
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=full_path,
                Body=screenshot_bytes,
                ContentType='image/png'
            )

            # Generate the URL
            url = f"https://{self.bucket_name}.s3.{
                self.region_name}.amazonaws.com/{full_path}"
            logger.info(f"Screenshot uploaded successfully to {url}")
            return url

        except ClientError as e:
            logger.error(f"Failed to upload screenshot to S3: {str(e)}")
            return None

    def get_presigned_url(self, object_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for an object

        Args:
            object_key: The key of the object in S3
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Presigned URL or None if generation fails
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None
