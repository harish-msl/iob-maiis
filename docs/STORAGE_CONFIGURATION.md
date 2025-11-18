# Storage Configuration Guide

**IOB MAIIS - MinIO & S3 Object Storage**

Comprehensive guide for configuring persistent file storage using MinIO (local/development) and AWS S3 (production).

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [MinIO Setup (Development)](#minio-setup-development)
5. [AWS S3 Setup (Production)](#aws-s3-setup-production)
6. [Configuration Reference](#configuration-reference)
7. [API Usage](#api-usage)
8. [Migration Guide](#migration-guide)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The IOB MAIIS storage system provides S3-compatible object storage for:
- 📄 **Documents** (PDFs, Word docs, text files)
- 🎵 **Audio files** (recordings, TTS outputs)
- 🖼️ **Images** (uploads, OCR sources)

### Key Features

- 🔄 **Provider Abstraction**: Easy switching between MinIO, S3, and local storage
- 🚀 **Production Ready**: Enterprise-grade reliability with MinIO/S3
- 💰 **Cost Effective**: MinIO for dev/staging, S3 for production
- 🔒 **Secure**: Server-side encryption, presigned URLs
- 📊 **Scalable**: Handle millions of files
- 🔧 **Easy Migration**: Migrate from local → MinIO → S3 seamlessly

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│               Storage Service (Unified API)              │
│  ┌────────────────────────────────────────────────────┐ │
│  │          Provider Factory                          │ │
│  └──────┬─────────────────┬──────────────────┬────────┘ │
│         │                 │                  │           │
│  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐  │
│  │   MinIO     │   │   AWS S3    │   │   Local     │  │
│  │  Provider   │   │  Provider   │   │  Provider   │  │
│  └─────────────┘   └─────────────┘   └─────────────┘  │
└─────────────────────────────────────────────────────────┘
         │                   │                  │
    ┌────▼────┐         ┌────▼────┐       ┌────▼────┐
    │ MinIO   │         │  AWS    │       │  Local  │
    │ Server  │         │   S3    │       │  Disk   │
    └─────────┘         └─────────┘       └─────────┘
```

### Storage Buckets/Folders

| Type | MinIO Bucket | S3 Prefix | Local Dir |
|------|--------------|-----------|-----------|
| **Documents** | `documents` | `documents/` | `documents/` |
| **Audio** | `audio` | `audio/` | `audio/` |
| **Images** | `images` | `images/` | `images/` |

### File Organization

```
documents/
  ├── user_1/
  │   ├── invoice.pdf
  │   └── report.docx
  ├── user_2/
  │   └── contract.pdf
  └── ...

audio/
  ├── user_1/
  │   ├── recording_123.mp3
  │   └── tts_response_456.mp3
  └── ...

images/
  ├── user_1/
  │   ├── receipt_scan.jpg
  │   └── id_document.png
  └── ...
```

---

## Quick Start

### Development Setup (MinIO)

**1. Start services with MinIO:**

```bash
# MinIO is included in docker-compose.yml
docker-compose up -d

# MinIO will be available at:
# - API: http://localhost:9000
# - Console: http://localhost:9001
# - Username: minioadmin
# - Password: minioadmin
```

**2. Configure backend (already set in docker-compose):**

```bash
# In backend/.env
STORAGE_PROVIDER=minio
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
```

**3. Verify storage:**

```bash
# Check health
curl http://localhost:8000/api/v1/storage/health

# Access MinIO console
open http://localhost:9001
```

### Production Setup (AWS S3)

**1. Create S3 bucket:**

```bash
# Using AWS CLI
aws s3 mb s3://iob-maiis-production --region us-east-1

# Enable versioning (recommended)
aws s3api put-bucket-versioning \
  --bucket iob-maiis-production \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket iob-maiis-production \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

**2. Create IAM policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::iob-maiis-production",
        "arn:aws:s3:::iob-maiis-production/*"
      ]
    }
  ]
}
```

**3. Configure backend:**

```bash
# In backend/.env
STORAGE_PROVIDER=s3
S3_REGION=us-east-1
S3_BUCKET=iob-maiis-production
S3_ACCESS_KEY=AKIA...
S3_SECRET_KEY=...
S3_USE_SSL=true
ENABLE_STORAGE_ENCRYPTION=true
```

---

## MinIO Setup (Development)

### Docker Compose Configuration

MinIO is already configured in `docker-compose.yml`:

```yaml
services:
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"  # API
      - "9001:9001"  # Console
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
```

### Automatic Bucket Creation

Buckets are automatically created by the `minio-setup` service:

```yaml
minio-setup:
  image: minio/mc:latest
  entrypoint: |
    mc alias set myminio http://minio:9000 minioadmin minioadmin
    mc mb myminio/documents --ignore-existing
    mc mb myminio/audio --ignore-existing
    mc mb myminio/images --ignore-existing
```

### MinIO Console Access

1. **Open browser**: http://localhost:9001
2. **Login**:
   - Username: `minioadmin`
   - Password: `minioadmin`
3. **Browse buckets**: Navigate to "Buckets" → Select bucket → Browse files

### MinIO CLI Usage

```bash
# Install mc (MinIO Client)
brew install minio/stable/mc  # macOS
# or download from: https://min.io/docs/minio/linux/reference/minio-mc.html

# Configure alias
mc alias set local http://localhost:9000 minioadmin minioadmin

# List buckets
mc ls local

# List files in documents bucket
mc ls local/documents

# Upload file
mc cp myfile.pdf local/documents/user_1/

# Download file
mc cp local/documents/user_1/myfile.pdf ./downloaded.pdf

# Remove file
mc rm local/documents/user_1/myfile.pdf
```

### Custom MinIO Configuration

To customize MinIO settings, update `.env`:

```bash
# Change credentials
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=SecurePassword123!

# Update in backend config
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=SecurePassword123!
```

---

## AWS S3 Setup (Production)

### Prerequisites

- AWS account
- AWS CLI installed and configured
- IAM permissions to create buckets and policies

### Step-by-Step Setup

**1. Create S3 Bucket:**

```bash
# Set variables
BUCKET_NAME="iob-maiis-production"
REGION="us-east-1"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region $REGION
```

**2. Configure Bucket Settings:**

```bash
# Block public access (recommended)
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      },
      "BucketKeyEnabled": true
    }]
  }'

# Set lifecycle policy (optional - auto-delete old files)
aws s3api put-bucket-lifecycle-configuration \
  --bucket $BUCKET_NAME \
  --lifecycle-configuration file://s3-lifecycle.json
```

**3. Create IAM User:**

```bash
# Create user
aws iam create-user --user-name iob-maiis-s3-user

# Attach policy
aws iam put-user-policy \
  --user-name iob-maiis-s3-user \
  --policy-name iob-maiis-s3-policy \
  --policy-document file://s3-policy.json

# Create access keys
aws iam create-access-key --user-name iob-maiis-s3-user
```

**4. Configure Backend:**

```bash
# Add to backend/.env
STORAGE_PROVIDER=s3
S3_REGION=us-east-1
S3_BUCKET=iob-maiis-production
S3_ACCESS_KEY=AKIA...  # From create-access-key output
S3_SECRET_KEY=...       # From create-access-key output
S3_USE_SSL=true
ENABLE_STORAGE_ENCRYPTION=true
```

### S3 Lifecycle Policy Example

Create `s3-lifecycle.json`:

```json
{
  "Rules": [
    {
      "Id": "DeleteOldTemporaryFiles",
      "Status": "Enabled",
      "Prefix": "temp/",
      "Expiration": {
        "Days": 7
      }
    },
    {
      "Id": "TransitionToIA",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "STANDARD_IA"
        }
      ]
    }
  ]
}
```

### S3 Cost Optimization

**1. Use Intelligent-Tiering:**

```bash
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket $BUCKET_NAME \
  --id AutoArchive \
  --intelligent-tiering-configuration '{
    "Id": "AutoArchive",
    "Status": "Enabled",
    "Tierings": [
      {
        "Days": 90,
        "AccessTier": "ARCHIVE_ACCESS"
      }
    ]
  }'
```

**2. Compress files before upload** (handled automatically by storage service)

**3. Use CloudFront CDN** for frequently accessed files

---

## Configuration Reference

### Environment Variables

```bash
# ============================================
# STORAGE PROVIDER SELECTION
# ============================================
STORAGE_PROVIDER=minio  # minio, s3, local

# ============================================
# MINIO CONFIGURATION
# ============================================
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET_DOCUMENTS=documents
MINIO_BUCKET_AUDIO=audio
MINIO_BUCKET_IMAGES=images
MINIO_REGION=us-east-1

# ============================================
# AWS S3 CONFIGURATION
# ============================================
S3_ENDPOINT=                    # Leave empty for AWS S3
S3_ACCESS_KEY=AKIA...
S3_SECRET_KEY=...
S3_REGION=us-east-1
S3_BUCKET=iob-maiis-production
S3_BUCKET_DOCUMENTS=documents
S3_BUCKET_AUDIO=audio
S3_BUCKET_IMAGES=images
S3_USE_SSL=true
S3_SIGNATURE_VERSION=s3v4

# ============================================
# STORAGE OPTIMIZATION
# ============================================
STORAGE_PRESIGNED_URL_EXPIRY=3600        # 1 hour
STORAGE_MAX_MULTIPART_SIZE=104857600     # 100MB
ENABLE_STORAGE_ENCRYPTION=true
STORAGE_RETENTION_DAYS=365               # 0 = forever

# ============================================
# FILE UPLOAD LIMITS
# ============================================
MAX_UPLOAD_SIZE=10485760                 # 10MB
MAX_FILE_SIZE_MB=10
```

### Configuration Scenarios

**Development (MinIO):**
```bash
STORAGE_PROVIDER=minio
MINIO_ENDPOINT=minio:9000
MINIO_SECURE=false
```

**Staging (MinIO with SSL):**
```bash
STORAGE_PROVIDER=minio
MINIO_ENDPOINT=minio.staging.example.com
MINIO_SECURE=true
```

**Production (AWS S3):**
```bash
STORAGE_PROVIDER=s3
S3_REGION=us-east-1
S3_BUCKET=iob-maiis-production
S3_USE_SSL=true
ENABLE_STORAGE_ENCRYPTION=true
```

**Local Development (No Docker):**
```bash
STORAGE_PROVIDER=local
UPLOAD_DIRECTORY=/data/documents
```

---

## API Usage

### Python Service API

```python
from app.services.storage_service import get_storage_service

# Get storage service
storage = get_storage_service()

# Upload document
result = await storage.upload_document(
    file_data=file_bytes,
    filename="invoice.pdf",
    user_id=user.id,
    content_type="application/pdf",
    metadata={"category": "invoice"}
)

# Returns:
# {
#   "url": "http://minio:9000/documents/user_1/invoice.pdf",
#   "object_name": "user_1/invoice.pdf",
#   "bucket": "documents",
#   "size": 102400,
#   "content_type": "application/pdf"
# }

# Download file
file_data = await storage.download_file(
    object_name="user_1/invoice.pdf",
    bucket="documents"
)

# Get presigned URL (temporary access)
url = await storage.get_presigned_url(
    object_name="user_1/invoice.pdf",
    bucket="documents",
    expiry=3600  # 1 hour
)

# Delete file
success = await storage.delete_file(
    object_name="user_1/invoice.pdf",
    bucket="documents"
)

# List user files
files = await storage.list_user_documents(user_id=1)

# Check health
health = await storage.check_health()
```

### REST API Endpoints

**Upload Document:**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "process_ocr=true"
```

**Download Document:**
```bash
curl -X GET "http://localhost:8000/api/documents/{id}/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output downloaded.pdf
```

**Get Presigned URL:**
```bash
curl -X GET "http://localhost:8000/api/documents/{id}/url" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**List Documents:**
```bash
curl -X GET "http://localhost:8000/api/documents" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Migration Guide

### Local → MinIO

**1. Configure MinIO:**
```bash
STORAGE_PROVIDER=minio
```

**2. Migrate existing files:**
```python
# Run migration script
python backend/scripts/migrate_storage.py --from local --to minio
```

**3. Verify migration:**
```bash
# Check MinIO console
open http://localhost:9001
```

### MinIO → AWS S3

**1. Create S3 bucket** (see AWS S3 Setup)

**2. Sync data:**
```bash
# Using mc (MinIO Client)
mc mirror local/documents s3/iob-maiis-production/documents
mc mirror local/audio s3/iob-maiis-production/audio
mc mirror local/images s3/iob-maiis-production/images

# Or using AWS CLI
aws s3 sync /path/to/minio/data s3://iob-maiis-production/
```

**3. Update configuration:**
```bash
STORAGE_PROVIDER=s3
S3_BUCKET=iob-maiis-production
```

**4. Update database paths** (if stored):
```sql
-- Update document paths
UPDATE documents 
SET file_path = REPLACE(file_path, '/uploads/', 's3://iob-maiis-production/documents/');
```

### Zero-Downtime Migration

**1. Dual-write approach:**
```python
# Write to both old and new storage
await old_storage.upload_file(...)
await new_storage.upload_file(...)
```

**2. Gradual migration:**
```python
# Migrate files in batches
for batch in get_file_batches():
    for file in batch:
        migrate_file(file)
    sleep(60)  # Rate limiting
```

**3. Switch reads:**
```python
# Read from new storage, fallback to old
try:
    return await new_storage.download_file(...)
except:
    return await old_storage.download_file(...)
```

---

## Best Practices

### Security

1. **Never commit credentials** to version control
   ```bash
   # Use environment variables or secrets manager
   export S3_ACCESS_KEY=...
   ```

2. **Enable server-side encryption**
   ```bash
   ENABLE_STORAGE_ENCRYPTION=true
   ```

3. **Use presigned URLs** for temporary access
   ```python
   url = await storage.get_presigned_url(object, bucket, expiry=300)
   ```

4. **Implement access controls**
   - User can only access their own files
   - Admin can access all files

5. **Rotate credentials** regularly
   ```bash
   # Rotate every 90 days
   aws iam create-access-key --user-name iob-maiis-s3-user
   aws iam delete-access-key --access-key-id OLD_KEY_ID
   ```

### Performance

1. **Use multipart upload** for large files (>5MB)
2. **Enable compression** for text files
3. **Use CDN (CloudFront)** for frequently accessed files
4. **Implement caching** for file metadata
5. **Batch operations** when possible

### Cost Optimization

1. **Use lifecycle policies** to archive old files
2. **Delete unnecessary files** regularly
3. **Compress files** before upload
4. **Use S3 Intelligent-Tiering** in production
5. **Monitor usage** with CloudWatch/MinIO metrics

### Reliability

1. **Enable versioning** to prevent data loss
2. **Implement backup strategy**
   ```bash
   # Daily backup to S3 Glacier
   aws s3 sync s3://iob-maiis-production/ s3://iob-maiis-backups/
   ```
3. **Use multiple regions** for critical data
4. **Monitor storage health**
5. **Test disaster recovery** procedures

---

## Troubleshooting

### Common Issues

**1. MinIO Connection Failed**

```
Error: MinIO endpoint not reachable
```

**Solution:**
```bash
# Check if MinIO is running
docker ps | grep minio

# Check network connectivity
docker network inspect iob_maiis_network

# Verify endpoint configuration
echo $MINIO_ENDPOINT

# Restart MinIO
docker-compose restart minio
```

**2. S3 Access Denied**

```
Error: Access Denied (403)
```

**Solution:**
```bash
# Verify credentials
aws sts get-caller-identity

# Check IAM policy
aws iam get-user-policy --user-name iob-maiis-s3-user --policy-name iob-maiis-s3-policy

# Test S3 access
aws s3 ls s3://iob-maiis-production/
```

**3. Upload Fails**

```
Error: File too large
```

**Solution:**
```bash
# Increase upload size limit
MAX_UPLOAD_SIZE=52428800  # 50MB

# For very large files, use multipart upload
STORAGE_MAX_MULTIPART_SIZE=104857600  # 100MB
```

**4. Bucket Not Found**

```
Error: The specified bucket does not exist
```

**Solution:**
```bash
# Create bucket manually
mc mb local/documents

# Or check bucket name
mc ls local
```

**5. Presigned URL Expired**

```
Error: Request has expired
```

**Solution:**
```python
# Increase expiry time
url = await storage.get_presigned_url(object, bucket, expiry=7200)  # 2 hours
```

### Debugging

**Enable debug logging:**
```python
import logging
logging.getLogger('minio').setLevel(logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.DEBUG)
```

**Check storage health:**
```bash
curl http://localhost:8000/api/v1/storage/health
```

**Verify file upload:**
```bash
# List files in bucket
mc ls local/documents/user_1/

# Check file info
mc stat local/documents/user_1/invoice.pdf
```

### Performance Issues

**Slow uploads:**
- Check network bandwidth
- Use multipart upload for large files
- Enable compression
- Upgrade storage provider tier

**High costs:**
- Review lifecycle policies
- Delete unused files
- Use S3 Intelligent-Tiering
- Compress files before upload

---

## Monitoring

### MinIO Metrics

```bash
# Access MinIO console
open http://localhost:9001

# View metrics:
# - Storage usage
# - Request rate
# - Bandwidth
# - Error rate
```

### S3 Metrics (CloudWatch)

```bash
# Enable S3 request metrics
aws s3api put-bucket-metrics-configuration \
  --bucket iob-maiis-production \
  --id EntireBucket \
  --metrics-configuration '{
    "Id": "EntireBucket",
    "Filter": {"Prefix": ""}
  }'

# View metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name NumberOfObjects \
  --dimensions Name=BucketName,Value=iob-maiis-production \
  --statistics Average \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --period 86400
```

### Prometheus Metrics (Custom)

```python
from prometheus_client import Counter, Histogram

upload_counter = Counter('storage_uploads_total', 'Total uploads')
upload_duration = Histogram('storage_upload_duration_seconds', 'Upload duration')
```

---

## Resources

### Documentation
- [MinIO Documentation](https://min.io/docs/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [MinIO Python Client](https://min.io/docs/minio/linux/developers/python/minio-py.html)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

### Tools
- [MinIO Console](http://localhost:9001)
- [MinIO Client (mc)](https://min.io/docs/minio/linux/reference/minio-mc.html)
- [AWS CLI](https://aws.amazon.com/cli/)
- [S3 Browser](https://s3browser.com/)

### Related Docs
- `docs/SPEECH_PROVIDERS.md` - Speech/TTS storage
- `backend/SPEECH_PROVIDERS_README.md` - Quick reference
- `docs/API_REFERENCE.md` - API documentation

---

**Last Updated**: 2025-01-17  
**Version**: 1.0.0  
**Maintainer**: IOB MAIIS Team