#!/usr/bin/env python3
"""
Storage Migration Script
Migrate files between storage providers (local → MinIO → S3)

Usage:
    python migrate_storage.py --from local --to minio
    python migrate_storage.py --from minio --to s3
    python migrate_storage.py --from local --to s3 --dry-run
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List, Tuple

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.db.base import Base
from app.models.document import Document
from app.services.storage_service import (
    LocalStorageProvider,
    MinioStorageProvider,
    S3StorageProvider,
)
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = get_settings()


class StorageMigration:
    """Handle storage migration between providers"""

    def __init__(self, source: str, destination: str, dry_run: bool = False):
        self.source_name = source
        self.destination_name = destination
        self.dry_run = dry_run

        # Initialize providers
        self.source_provider = self._create_provider(source)
        self.destination_provider = self._create_provider(destination)

        # Initialize database
        self.engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))
        SessionLocal = sessionmaker(bind=self.engine)
        self.db = SessionLocal()

        # Statistics
        self.stats = {
            "total_files": 0,
            "migrated": 0,
            "skipped": 0,
            "failed": 0,
            "total_size": 0,
        }

    def _create_provider(self, provider_name: str):
        """Create storage provider instance"""
        if provider_name == "local":
            return LocalStorageProvider()
        elif provider_name == "minio":
            return MinioStorageProvider()
        elif provider_name == "s3":
            return S3StorageProvider()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    async def migrate_file(
        self,
        object_name: str,
        source_bucket: str,
        dest_bucket: str,
    ) -> bool:
        """
        Migrate a single file

        Args:
            object_name: File path/key
            source_bucket: Source bucket name
            dest_bucket: Destination bucket name

        Returns:
            True if successful
        """
        try:
            logger.info(f"Migrating: {source_bucket}/{object_name}")

            # Download from source
            file_data = await self.source_provider.download_file(
                object_name, source_bucket
            )

            # Get file info from source
            try:
                file_info = await self.source_provider.get_file_info(
                    object_name, source_bucket
                )
                content_type = file_info.get("content_type")
                metadata = file_info.get("metadata", {})
            except Exception:
                content_type = "application/octet-stream"
                metadata = {}

            if self.dry_run:
                logger.info(
                    f"[DRY RUN] Would migrate {len(file_data)} bytes to {dest_bucket}/{object_name}"
                )
                self.stats["migrated"] += 1
                self.stats["total_size"] += len(file_data)
                return True

            # Upload to destination
            await self.destination_provider.upload_file(
                file_data=file_data,
                object_name=object_name,
                bucket=dest_bucket,
                content_type=content_type,
                metadata=metadata,
            )

            self.stats["migrated"] += 1
            self.stats["total_size"] += len(file_data)

            logger.success(f"✓ Migrated {object_name} ({len(file_data)} bytes)")

            return True

        except Exception as e:
            logger.error(f"✗ Failed to migrate {object_name}: {str(e)}")
            self.stats["failed"] += 1
            return False

    async def migrate_bucket(
        self,
        source_bucket: str,
        dest_bucket: str,
        prefix: str = None,
    ):
        """
        Migrate all files in a bucket

        Args:
            source_bucket: Source bucket name
            dest_bucket: Destination bucket name
            prefix: Optional prefix to filter files
        """
        logger.info(f"Migrating bucket: {source_bucket} → {dest_bucket}")

        # List files in source bucket
        files = await self.source_provider.list_files(source_bucket, prefix)

        if not files:
            logger.warning(f"No files found in {source_bucket}")
            return

        logger.info(f"Found {len(files)} files to migrate")
        self.stats["total_files"] += len(files)

        # Migrate each file
        for file_info in files:
            object_name = file_info["name"]

            # Check if file already exists in destination
            exists = await self.destination_provider.file_exists(
                object_name, dest_bucket
            )

            if exists:
                logger.warning(f"Skipping {object_name} (already exists)")
                self.stats["skipped"] += 1
                continue

            # Migrate file
            await self.migrate_file(object_name, source_bucket, dest_bucket)

            # Small delay to avoid overwhelming the services
            await asyncio.sleep(0.1)

    async def migrate_all(self):
        """Migrate all buckets (documents, audio, images)"""
        logger.info(f"Starting migration: {self.source_name} → {self.destination_name}")

        if self.dry_run:
            logger.warning("DRY RUN MODE - No files will be actually migrated")

        # Define bucket mappings
        bucket_mappings = self._get_bucket_mappings()

        # Migrate each bucket type
        for source_bucket, dest_bucket in bucket_mappings:
            try:
                await self.migrate_bucket(source_bucket, dest_bucket)
            except Exception as e:
                logger.error(f"Failed to migrate bucket {source_bucket}: {str(e)}")

        # Update database paths if needed
        if not self.dry_run:
            await self.update_database_paths()

    def _get_bucket_mappings(self) -> List[Tuple[str, str]]:
        """Get bucket name mappings based on providers"""
        if self.source_name == "local":
            source_docs = "documents"
            source_audio = "audio"
            source_images = "images"
        elif self.source_name == "minio":
            source_docs = settings.MINIO_BUCKET_DOCUMENTS
            source_audio = settings.MINIO_BUCKET_AUDIO
            source_images = settings.MINIO_BUCKET_IMAGES
        else:  # s3
            source_docs = settings.S3_BUCKET
            source_audio = settings.S3_BUCKET
            source_images = settings.S3_BUCKET

        if self.destination_name == "local":
            dest_docs = "documents"
            dest_audio = "audio"
            dest_images = "images"
        elif self.destination_name == "minio":
            dest_docs = settings.MINIO_BUCKET_DOCUMENTS
            dest_audio = settings.MINIO_BUCKET_AUDIO
            dest_images = settings.MINIO_BUCKET_IMAGES
        else:  # s3
            dest_docs = settings.S3_BUCKET
            dest_audio = settings.S3_BUCKET
            dest_images = settings.S3_BUCKET

        return [
            (source_docs, dest_docs),
            (source_audio, dest_audio),
            (source_images, dest_images),
        ]

    async def update_database_paths(self):
        """Update file paths in database"""
        logger.info("Updating database paths...")

        try:
            # Update document paths
            documents = self.db.query(Document).all()

            for doc in documents:
                old_path = doc.file_path

                # Update path based on destination provider
                if self.destination_name == "minio":
                    # Update to MinIO format
                    new_path = old_path.replace("/uploads/", "")
                    new_path = old_path.replace("/data/documents/", "")
                elif self.destination_name == "s3":
                    # Update to S3 format
                    bucket = settings.S3_BUCKET
                    prefix = settings.S3_BUCKET_DOCUMENTS
                    new_path = f"s3://{bucket}/{prefix}/{old_path}"
                else:
                    # Local format
                    new_path = old_path

                if new_path != old_path:
                    doc.file_path = new_path
                    logger.info(f"Updated path: {old_path} → {new_path}")

            self.db.commit()
            logger.success("✓ Database paths updated")

        except Exception as e:
            logger.error(f"Failed to update database paths: {str(e)}")
            self.db.rollback()

    def print_summary(self):
        """Print migration summary"""
        logger.info("=" * 60)
        logger.info("Migration Summary")
        logger.info("=" * 60)
        logger.info(f"Source: {self.source_name}")
        logger.info(f"Destination: {self.destination_name}")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        logger.info("-" * 60)
        logger.info(f"Total files found: {self.stats['total_files']}")
        logger.success(f"Successfully migrated: {self.stats['migrated']}")
        logger.warning(f"Skipped (already exist): {self.stats['skipped']}")
        logger.error(f"Failed: {self.stats['failed']}")
        logger.info(f"Total size: {self.stats['total_size'] / 1024 / 1024:.2f} MB")
        logger.info("=" * 60)

        if self.stats["failed"] > 0:
            logger.error(
                "⚠️  Some files failed to migrate. Check logs above for details."
            )
            return False
        else:
            logger.success("✓ Migration completed successfully!")
            return True


async def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description="Migrate storage between providers")

    parser.add_argument(
        "--from",
        dest="source",
        required=True,
        choices=["local", "minio", "s3"],
        help="Source storage provider",
    )

    parser.add_argument(
        "--to",
        dest="destination",
        required=True,
        choices=["local", "minio", "s3"],
        help="Destination storage provider",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run (no actual migration)",
    )

    parser.add_argument(
        "--bucket",
        help="Migrate only specific bucket (documents, audio, images)",
        choices=["documents", "audio", "images"],
    )

    parser.add_argument(
        "--prefix",
        help="Migrate only files with this prefix (e.g., user_1/)",
    )

    args = parser.parse_args()

    # Validate
    if args.source == args.destination:
        logger.error("Source and destination must be different!")
        return 1

    # Create migration instance
    migration = StorageMigration(
        source=args.source,
        destination=args.destination,
        dry_run=args.dry_run,
    )

    # Run migration
    try:
        if args.bucket:
            # Migrate single bucket
            source_bucket = args.bucket
            dest_bucket = args.bucket
            await migration.migrate_bucket(source_bucket, dest_bucket, args.prefix)
        else:
            # Migrate all buckets
            await migration.migrate_all()

        # Print summary
        success = migration.print_summary()

        return 0 if success else 1

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Migration interrupted by user")
        migration.print_summary()
        return 1

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
