"""
Storage Service
S3-compatible object storage for documents, images, and audio files
Supports MinIO (local/dev) and AWS S3 (production)
"""

import io
import os
from abc import ABC, abstractmethod
from datetime import timedelta
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple

from loguru import logger
from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

settings = get_settings()


# ============================================
# BASE STORAGE INTERFACE
# ============================================


class StorageProvider(ABC):
    """Abstract base class for storage providers"""

    @abstractmethod
    async def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        bucket: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Upload file to storage

        Args:
            file_data: File bytes
            object_name: Object name/path in storage
            bucket: Bucket name
            content_type: MIME type
            metadata: Additional metadata

        Returns:
            Object URL or path
        """
        pass

    @abstractmethod
    async def download_file(self, object_name: str, bucket: str) -> bytes:
        """
        Download file from storage

        Args:
            object_name: Object name/path
            bucket: Bucket name

        Returns:
            File bytes
        """
        pass

    @abstractmethod
    async def delete_file(self, object_name: str, bucket: str) -> bool:
        """
        Delete file from storage

        Args:
            object_name: Object name/path
            bucket: Bucket name

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def file_exists(self, object_name: str, bucket: str) -> bool:
        """Check if file exists"""
        pass

    @abstractmethod
    async def list_files(
        self, bucket: str, prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in bucket"""
        pass

    @abstractmethod
    async def get_presigned_url(
        self, object_name: str, bucket: str, expiry: int = 3600
    ) -> str:
        """Generate presigned URL for temporary access"""
        pass

    @abstractmethod
    async def get_file_info(self, object_name: str, bucket: str) -> Dict[str, Any]:
        """Get file metadata and info"""
        pass


# ============================================
# MINIO STORAGE PROVIDER
# ============================================


class MinioStorageProvider(StorageProvider):
    """MinIO storage provider (S3-compatible)"""

    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.secure = settings.MINIO_SECURE
        self.region = settings.MINIO_REGION

        # Initialize MinIO client
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
            region=self.region,
        )

        logger.info(
            f"MinIO storage initialized: {self.endpoint} (secure={self.secure})"
        )

    async def _ensure_bucket_exists(self, bucket: str):
        """Ensure bucket exists, create if not"""
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket, location=self.region)
                logger.info(f"Created MinIO bucket: {bucket}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {str(e)}")
            raise

    async def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        bucket: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Upload file to MinIO"""
        try:
            await self._ensure_bucket_exists(bucket)

            # Prepare file stream
            file_stream = io.BytesIO(file_data)
            file_size = len(file_data)

            # Upload
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=file_stream,
                length=file_size,
                content_type=content_type or "application/octet-stream",
                metadata=metadata or {},
            )

            # Generate URL
            url = f"http{'s' if self.secure else ''}://{self.endpoint}/{bucket}/{object_name}"

            logger.info(
                f"Uploaded file to MinIO: {bucket}/{object_name} ({file_size} bytes)"
            )

            return url

        except S3Error as e:
            logger.error(f"MinIO upload failed: {str(e)}")
            raise Exception(f"Upload failed: {str(e)}")

    async def download_file(self, object_name: str, bucket: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()

            logger.info(f"Downloaded file from MinIO: {bucket}/{object_name}")
            return data

        except S3Error as e:
            logger.error(f"MinIO download failed: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")

    async def delete_file(self, object_name: str, bucket: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted file from MinIO: {bucket}/{object_name}")
            return True

        except S3Error as e:
            logger.error(f"MinIO delete failed: {str(e)}")
            return False

    async def file_exists(self, object_name: str, bucket: str) -> bool:
        """Check if file exists in MinIO"""
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error:
            return False

    async def list_files(
        self, bucket: str, prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in MinIO bucket"""
        try:
            objects = self.client.list_objects(
                bucket, prefix=prefix or "", recursive=True
            )

            files = []
            for obj in objects:
                files.append(
                    {
                        "name": obj.object_name,
                        "size": obj.size,
                        "last_modified": obj.last_modified.isoformat()
                        if obj.last_modified
                        else None,
                        "etag": obj.etag,
                        "content_type": obj.content_type,
                    }
                )

            return files

        except S3Error as e:
            logger.error(f"MinIO list failed: {str(e)}")
            return []

    async def get_presigned_url(
        self, object_name: str, bucket: str, expiry: int = 3600
    ) -> str:
        """Generate presigned URL for temporary access"""
        try:
            url = self.client.presigned_get_object(
                bucket, object_name, expires=timedelta(seconds=expiry)
            )
            return url

        except S3Error as e:
            logger.error(f"MinIO presigned URL generation failed: {str(e)}")
            raise Exception(f"Presigned URL generation failed: {str(e)}")

    async def get_file_info(self, object_name: str, bucket: str) -> Dict[str, Any]:
        """Get file metadata and info"""
        try:
            stat = self.client.stat_object(bucket, object_name)

            return {
                "name": object_name,
                "size": stat.size,
                "last_modified": stat.last_modified.isoformat()
                if stat.last_modified
                else None,
                "etag": stat.etag,
                "content_type": stat.content_type,
                "metadata": stat.metadata,
            }

        except S3Error as e:
            logger.error(f"MinIO stat failed: {str(e)}")
            raise Exception(f"File not found: {str(e)}")


# ============================================
# AWS S3 STORAGE PROVIDER
# ============================================


class S3StorageProvider(StorageProvider):
    """AWS S3 storage provider"""

    def __init__(self):
        try:
            import boto3
            from botocore.config import Config
        except ImportError:
            raise ImportError(
                "boto3 is required for S3 storage. Install with: pip install boto3"
            )

        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.region = settings.S3_REGION
        self.bucket = settings.S3_BUCKET
        self.endpoint = settings.S3_ENDPOINT
        self.use_ssl = settings.S3_USE_SSL

        # Initialize S3 client
        config = Config(
            region_name=self.region,
            signature_version=settings.S3_SIGNATURE_VERSION,
            retries={"max_attempts": 3, "mode": "adaptive"},
        )

        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint,
            config=config,
            use_ssl=self.use_ssl,
        )

        logger.info(f"S3 storage initialized: {self.region}/{self.bucket}")

    async def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        bucket: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Upload file to S3"""
        try:
            file_stream = io.BytesIO(file_data)

            extra_args = {
                "ContentType": content_type or "application/octet-stream",
            }

            if metadata:
                extra_args["Metadata"] = metadata

            if settings.ENABLE_STORAGE_ENCRYPTION:
                extra_args["ServerSideEncryption"] = "AES256"

            self.client.upload_fileobj(
                file_stream, bucket, object_name, ExtraArgs=extra_args
            )

            url = f"https://{bucket}.s3.{self.region}.amazonaws.com/{object_name}"

            logger.info(f"Uploaded file to S3: {bucket}/{object_name}")

            return url

        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise Exception(f"Upload failed: {str(e)}")

    async def download_file(self, object_name: str, bucket: str) -> bytes:
        """Download file from S3"""
        try:
            file_stream = io.BytesIO()
            self.client.download_fileobj(bucket, object_name, file_stream)
            file_stream.seek(0)
            data = file_stream.read()

            logger.info(f"Downloaded file from S3: {bucket}/{object_name}")
            return data

        except Exception as e:
            logger.error(f"S3 download failed: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")

    async def delete_file(self, object_name: str, bucket: str) -> bool:
        """Delete file from S3"""
        try:
            self.client.delete_object(Bucket=bucket, Key=object_name)
            logger.info(f"Deleted file from S3: {bucket}/{object_name}")
            return True

        except Exception as e:
            logger.error(f"S3 delete failed: {str(e)}")
            return False

    async def file_exists(self, object_name: str, bucket: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.client.head_object(Bucket=bucket, Key=object_name)
            return True
        except Exception:
            return False

    async def list_files(
        self, bucket: str, prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in S3 bucket"""
        try:
            response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix or "")

            files = []
            for obj in response.get("Contents", []):
                files.append(
                    {
                        "name": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                        "etag": obj["ETag"],
                    }
                )

            return files

        except Exception as e:
            logger.error(f"S3 list failed: {str(e)}")
            return []

    async def get_presigned_url(
        self, object_name: str, bucket: str, expiry: int = 3600
    ) -> str:
        """Generate presigned URL for temporary access"""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": object_name},
                ExpiresIn=expiry,
            )
            return url

        except Exception as e:
            logger.error(f"S3 presigned URL generation failed: {str(e)}")
            raise Exception(f"Presigned URL generation failed: {str(e)}")

    async def get_file_info(self, object_name: str, bucket: str) -> Dict[str, Any]:
        """Get file metadata and info"""
        try:
            response = self.client.head_object(Bucket=bucket, Key=object_name)

            return {
                "name": object_name,
                "size": response["ContentLength"],
                "last_modified": response["LastModified"].isoformat(),
                "etag": response["ETag"],
                "content_type": response.get("ContentType"),
                "metadata": response.get("Metadata", {}),
            }

        except Exception as e:
            logger.error(f"S3 head failed: {str(e)}")
            raise Exception(f"File not found: {str(e)}")


# ============================================
# LOCAL STORAGE PROVIDER
# ============================================


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider (for development)"""

    def __init__(self):
        self.base_path = Path(settings.UPLOAD_DIRECTORY)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage initialized: {self.base_path}")

    def _get_file_path(self, bucket: str, object_name: str) -> Path:
        """Get full file path"""
        bucket_path = self.base_path / bucket
        bucket_path.mkdir(parents=True, exist_ok=True)
        return bucket_path / object_name

    async def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        bucket: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Upload file to local storage"""
        try:
            file_path = self._get_file_path(bucket, object_name)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(file_data)

            logger.info(f"Uploaded file to local storage: {file_path}")

            return str(file_path)

        except Exception as e:
            logger.error(f"Local upload failed: {str(e)}")
            raise Exception(f"Upload failed: {str(e)}")

    async def download_file(self, object_name: str, bucket: str) -> bytes:
        """Download file from local storage"""
        try:
            file_path = self._get_file_path(bucket, object_name)

            with open(file_path, "rb") as f:
                data = f.read()

            logger.info(f"Downloaded file from local storage: {file_path}")
            return data

        except Exception as e:
            logger.error(f"Local download failed: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")

    async def delete_file(self, object_name: str, bucket: str) -> bool:
        """Delete file from local storage"""
        try:
            file_path = self._get_file_path(bucket, object_name)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file from local storage: {file_path}")
                return True
            return False

        except Exception as e:
            logger.error(f"Local delete failed: {str(e)}")
            return False

    async def file_exists(self, object_name: str, bucket: str) -> bool:
        """Check if file exists in local storage"""
        file_path = self._get_file_path(bucket, object_name)
        return file_path.exists()

    async def list_files(
        self, bucket: str, prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in local storage"""
        try:
            bucket_path = self.base_path / bucket
            if not bucket_path.exists():
                return []

            files = []
            pattern = f"{prefix}*" if prefix else "*"

            for file_path in bucket_path.rglob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append(
                        {
                            "name": str(file_path.relative_to(bucket_path)),
                            "size": stat.st_size,
                            "last_modified": stat.st_mtime,
                        }
                    )

            return files

        except Exception as e:
            logger.error(f"Local list failed: {str(e)}")
            return []

    async def get_presigned_url(
        self, object_name: str, bucket: str, expiry: int = 3600
    ) -> str:
        """Generate presigned URL (returns local path for local storage)"""
        file_path = self._get_file_path(bucket, object_name)
        return str(file_path)

    async def get_file_info(self, object_name: str, bucket: str) -> Dict[str, Any]:
        """Get file metadata and info"""
        try:
            file_path = self._get_file_path(bucket, object_name)
            stat = file_path.stat()

            return {
                "name": object_name,
                "size": stat.st_size,
                "last_modified": stat.st_mtime,
                "path": str(file_path),
            }

        except Exception as e:
            logger.error(f"Local stat failed: {str(e)}")
            raise Exception(f"File not found: {str(e)}")


# ============================================
# STORAGE SERVICE
# ============================================


class StorageService:
    """
    Unified storage service
    Manages document, audio, and image storage across different providers
    """

    def __init__(self):
        self.provider_name = settings.STORAGE_PROVIDER
        self._init_provider()
        self._init_buckets()

    def _init_provider(self):
        """Initialize storage provider based on configuration"""
        if self.provider_name == "minio":
            self.provider = MinioStorageProvider()
        elif self.provider_name == "s3":
            self.provider = S3StorageProvider()
        elif self.provider_name == "local":
            self.provider = LocalStorageProvider()
        else:
            logger.warning(
                f"Unknown storage provider '{self.provider_name}', using local"
            )
            self.provider = LocalStorageProvider()

        logger.info(f"Storage service initialized with provider: {self.provider_name}")

    def _init_buckets(self):
        """Initialize bucket names based on provider"""
        if self.provider_name == "minio":
            self.bucket_documents = settings.MINIO_BUCKET_DOCUMENTS
            self.bucket_audio = settings.MINIO_BUCKET_AUDIO
            self.bucket_images = settings.MINIO_BUCKET_IMAGES
        elif self.provider_name == "s3":
            # For S3, use prefixes within single bucket
            self.bucket_documents = settings.S3_BUCKET
            self.bucket_audio = settings.S3_BUCKET
            self.bucket_images = settings.S3_BUCKET
            # Store prefixes for S3
            self.prefix_documents = settings.S3_BUCKET_DOCUMENTS
            self.prefix_audio = settings.S3_BUCKET_AUDIO
            self.prefix_images = settings.S3_BUCKET_IMAGES
        else:
            # Local storage uses directories
            self.bucket_documents = "documents"
            self.bucket_audio = "audio"
            self.bucket_images = "images"

    def _add_s3_prefix(self, object_name: str, file_type: str) -> str:
        """Add S3 prefix if using S3 provider"""
        if self.provider_name == "s3":
            if file_type == "document":
                return f"{self.prefix_documents}/{object_name}"
            elif file_type == "audio":
                return f"{self.prefix_audio}/{object_name}"
            elif file_type == "image":
                return f"{self.prefix_images}/{object_name}"
        return object_name

    async def upload_document(
        self,
        file_data: bytes,
        filename: str,
        user_id: int,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Upload document file

        Args:
            file_data: File bytes
            filename: Original filename
            user_id: User ID
            content_type: MIME type
            metadata: Additional metadata

        Returns:
            Dict with upload info (url, path, size, etc.)
        """
        # Generate object name with user namespace
        object_name = f"user_{user_id}/{filename}"
        object_name = self._add_s3_prefix(object_name, "document")

        # Add user_id to metadata
        meta = metadata or {}
        meta["user_id"] = str(user_id)
        meta["original_filename"] = filename

        url = await self.provider.upload_file(
            file_data=file_data,
            object_name=object_name,
            bucket=self.bucket_documents,
            content_type=content_type,
            metadata=meta,
        )

        return {
            "url": url,
            "object_name": object_name,
            "bucket": self.bucket_documents,
            "size": len(file_data),
            "content_type": content_type,
        }

    async def upload_audio(
        self,
        file_data: bytes,
        filename: str,
        user_id: int,
        content_type: Optional[str] = "audio/mpeg",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Upload audio file"""
        object_name = f"user_{user_id}/{filename}"
        object_name = self._add_s3_prefix(object_name, "audio")

        meta = metadata or {}
        meta["user_id"] = str(user_id)
        meta["original_filename"] = filename

        url = await self.provider.upload_file(
            file_data=file_data,
            object_name=object_name,
            bucket=self.bucket_audio,
            content_type=content_type,
            metadata=meta,
        )

        return {
            "url": url,
            "object_name": object_name,
            "bucket": self.bucket_audio,
            "size": len(file_data),
            "content_type": content_type,
        }

    async def upload_image(
        self,
        file_data: bytes,
        filename: str,
        user_id: int,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Upload image file"""
        object_name = f"user_{user_id}/{filename}"
        object_name = self._add_s3_prefix(object_name, "image")

        meta = metadata or {}
        meta["user_id"] = str(user_id)
        meta["original_filename"] = filename

        url = await self.provider.upload_file(
            file_data=file_data,
            object_name=object_name,
            bucket=self.bucket_images,
            content_type=content_type,
            metadata=meta,
        )

        return {
            "url": url,
            "object_name": object_name,
            "bucket": self.bucket_images,
            "size": len(file_data),
            "content_type": content_type,
        }

    async def download_file(self, object_name: str, bucket: str) -> bytes:
        """Download file from storage"""
        return await self.provider.download_file(object_name, bucket)

    async def delete_file(self, object_name: str, bucket: str) -> bool:
        """Delete file from storage"""
        return await self.provider.delete_file(object_name, bucket)

    async def file_exists(self, object_name: str, bucket: str) -> bool:
        """Check if file exists"""
        return await self.provider.file_exists(object_name, bucket)

    async def get_presigned_url(
        self, object_name: str, bucket: str, expiry: Optional[int] = None
    ) -> str:
        """Get presigned URL for temporary access"""
        expiry = expiry or settings.STORAGE_PRESIGNED_URL_EXPIRY
        return await self.provider.get_presigned_url(object_name, bucket, expiry)

    async def get_file_info(self, object_name: str, bucket: str) -> Dict[str, Any]:
        """Get file metadata"""
        return await self.provider.get_file_info(object_name, bucket)

    async def list_user_documents(self, user_id: int) -> List[Dict[str, Any]]:
        """List all documents for a user"""
        prefix = f"user_{user_id}/"
        if self.provider_name == "s3":
            prefix = f"{self.prefix_documents}/{prefix}"
        return await self.provider.list_files(self.bucket_documents, prefix)

    async def list_user_audio(self, user_id: int) -> List[Dict[str, Any]]:
        """List all audio files for a user"""
        prefix = f"user_{user_id}/"
        if self.provider_name == "s3":
            prefix = f"{self.prefix_audio}/{prefix}"
        return await self.provider.list_files(self.bucket_audio, prefix)

    async def list_user_images(self, user_id: int) -> List[Dict[str, Any]]:
        """List all images for a user"""
        prefix = f"user_{user_id}/"
        if self.provider_name == "s3":
            prefix = f"{self.prefix_images}/{prefix}"
        return await self.provider.list_files(self.bucket_images, prefix)

    async def check_health(self) -> Dict[str, Any]:
        """Check storage service health"""
        health = {
            "provider": self.provider_name,
            "status": "unknown",
        }

        try:
            # Try to list files in documents bucket
            await self.provider.list_files(self.bucket_documents, prefix="")
            health["status"] = "healthy"

        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)

        return health


# ============================================
# SINGLETON INSTANCE
# ============================================

_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """
    Get singleton instance of storage service

    Returns:
        StorageService instance
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
