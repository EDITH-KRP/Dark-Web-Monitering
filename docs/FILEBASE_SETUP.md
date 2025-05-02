# Setting Up Filebase for Dark Web Monitoring Tool

This guide explains how to set up Filebase as a decentralized storage solution for the Dark Web Monitoring Tool.

## What is Filebase?

Filebase is a decentralized storage platform that uses IPFS, Sia, or Filecoin as the underlying storage layer. It provides an S3-compatible API, making it easy to integrate with existing applications.

## Why Use Filebase?

- **Decentralized**: Data is stored across a distributed network, not on centralized servers
- **Immutable**: Once stored, data cannot be modified or tampered with
- **Permanent**: Data is stored permanently (as long as you maintain your account)
- **S3-Compatible**: Uses the familiar Amazon S3 API
- **Cost-Effective**: Often cheaper than traditional cloud storage

## Setting Up Filebase

### 1. Create a Filebase Account

1. Go to [Filebase.com](https://filebase.com/) and sign up for an account
2. Verify your email address

### 2. Create a Bucket

1. Log in to your Filebase account
2. Navigate to the "Buckets" section
3. Click "Create Bucket"
4. Name your bucket (e.g., "darkweb-monitoring")
5. Select the storage network (IPFS, Sia, or Filecoin)
6. Click "Create"

### 3. Generate Access Keys

1. Navigate to the "Access Keys" section
2. Click "Create Access Key"
3. Give your key a name (e.g., "darkweb-monitoring-key")
4. Click "Create"
5. **Important**: Save both the Access Key and Secret Key securely. You won't be able to view the Secret Key again.

### 4. Configure the Dark Web Monitoring Tool

1. Open the `.env` file in the `backend` directory
2. Update the Filebase configuration:

```
# Filebase Configuration
FILEBASE_BUCKET=your-bucket-name
FILEBASE_ACCESS_KEY=your-access-key
FILEBASE_SECRET_KEY=your-secret-key
FILEBASE_ENDPOINT=https://s3.filebase.com
STORAGE_TYPE=filebase
```

3. Save the file

## Using Filebase in the Dark Web Monitoring Tool

The tool now includes several API endpoints for working with Filebase:

### Upload Data to Filebase

```
POST /upload-to-filebase
```

Request body:
```json
{
  "data_type": "crawl_results",
  "data": [
    {
      "url": "http://example.onion",
      "title": "Example Site",
      "description": "An example dark web site"
    }
  ]
}
```

### List Data in Filebase

```
GET /filebase-data?data_type=crawl_results&limit=100
```

### Get Data from Filebase

```
GET /filebase-data/{data_id}?data_type=crawl_results
```

### Delete Data from Filebase

```
DELETE /filebase-data/{data_id}?data_type=crawl_results
```

## Fallback to Local Storage

If Filebase is not configured or if there's an error connecting to Filebase, the tool will automatically fall back to local storage. Data will be stored in the `backend/data_storage` directory.

## Troubleshooting

### Cannot Connect to Filebase

- Verify your Access Key and Secret Key are correct
- Check that your bucket exists and is accessible
- Ensure your internet connection is working

### Permission Denied

- Verify that your Access Key has the necessary permissions
- Check that your bucket policy allows the operations you're trying to perform

### Data Not Found

- Verify that you're using the correct data ID
- Check that you're using the correct data type
- Ensure the data hasn't been deleted

## Additional Resources

- [Filebase Documentation](https://docs.filebase.com/)
- [S3 API Reference](https://docs.filebase.com/api-documentation/s3-compatible-api)
- [IPFS Documentation](https://docs.ipfs.io/)
- [Sia Documentation](https://sia.tech/docs/)
- [Filecoin Documentation](https://docs.filecoin.io/)