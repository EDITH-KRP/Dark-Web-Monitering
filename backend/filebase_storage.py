"""
Filebase storage module for the Dark Web Monitoring Tool.
This module provides functionality to store and retrieve data using Filebase,
a decentralized storage platform built on IPFS, Sia, or Filecoin.
"""

import os
import json
import time
import uuid
import requests
import base64
import boto3
from botocore.client import Config
from pathlib import Path
import config
from logger import get_logger

# Get module-specific logger
logger = get_logger('filebase_storage')

# Filebase configuration
FILEBASE_BUCKET = os.getenv('FILEBASE_BUCKET', 'darkweb-monitoring')
FILEBASE_ACCESS_KEY = os.getenv('FILEBASE_ACCESS_KEY', '')
FILEBASE_SECRET_KEY = os.getenv('FILEBASE_SECRET_KEY', '')
FILEBASE_ENDPOINT = os.getenv('FILEBASE_ENDPOINT', 'https://s3.filebase.com')

# Local storage directory for when Filebase is not configured
LOCAL_STORAGE_DIR = config.BASE_DIR / 'data_storage'

def is_filebase_configured():
    """Check if Filebase is properly configured"""
    is_configured = FILEBASE_ACCESS_KEY and FILEBASE_SECRET_KEY
    
    # In production mode, we require Filebase to be configured
    if os.environ.get("DARK_WEB_DEV_MODE") == "0" and not is_configured:
        logger.error("Filebase is not configured but is required in production mode")
        raise Exception("Filebase storage is required in production mode but API keys are not configured")
        
    return is_configured

def save_to_filebase(data, data_type='crawl_results'):
    """
    Save data to Filebase (or local storage if Filebase is not configured)
    
    Args:
        data: The data to save (will be converted to JSON)
        data_type: Type of data (used for organizing storage)
        
    Returns:
        dict: Information about the saved data including CID if using Filebase
    """
    # Generate a unique ID for this data
    data_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    # Add metadata
    metadata = {
        'id': data_id,
        'timestamp': timestamp,
        'timestamp_readable': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
        'data_type': data_type,
        'record_count': len(data) if isinstance(data, list) else 1
    }
    
    # Prepare the full data object
    full_data = {
        'metadata': metadata,
        'data': data
    }
    
    # Convert to JSON
    json_data = json.dumps(full_data, indent=2)
    
    # If Filebase is configured, use it
    if is_filebase_configured():
        try:
            logger.info(f"Saving data to Filebase, type: {data_type}, id: {data_id}")
            
            # Create the S3-compatible request
            filename = f"{data_type}_{data_id}.json"
            
            # Use boto3 to upload to Filebase (S3-compatible API)
            try:
                # Create an S3 client with Filebase endpoint
                s3_client = boto3.client(
                    's3',
                    endpoint_url=FILEBASE_ENDPOINT,
                    aws_access_key_id=FILEBASE_ACCESS_KEY,
                    aws_secret_access_key=FILEBASE_SECRET_KEY,
                    config=Config(signature_version='s3v4')
                )
                
                # Upload the file
                response = s3_client.put_object(
                    Bucket=FILEBASE_BUCKET,
                    Key=filename,
                    Body=json_data,
                    ContentType='application/json'
                )
                
                logger.info(f"Successfully saved to Filebase: {filename}")
                
                # Get the ETag (entity tag) which can be used as a CID
                cid = response.get('ETag', '').strip('"')
                
                return {
                    'success': True,
                    'storage': 'filebase',
                    'id': data_id,
                    'filename': filename,
                    'cid': cid,
                    'url': f"{FILEBASE_ENDPOINT}/{FILEBASE_BUCKET}/{filename}",
                    'timestamp': timestamp
                }
            else:
                logger.error(f"Failed to save to Filebase: {response.status_code}, {response.text}")
                # Fall back to local storage
                return _save_to_local_storage(json_data, data_type, data_id, timestamp)
                
        except Exception as e:
            logger.error(f"Error saving to Filebase: {e}")
            # Fall back to local storage
            return _save_to_local_storage(json_data, data_type, data_id, timestamp)
    else:
        # Use local storage
        logger.info(f"Filebase not configured, saving to local storage: {data_type}, {data_id}")
        return _save_to_local_storage(json_data, data_type, data_id, timestamp)

def _save_to_local_storage(json_data, data_type, data_id, timestamp):
    """Save data to local storage"""
    try:
        # Ensure the directory exists
        storage_dir = LOCAL_STORAGE_DIR / data_type
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the filename
        filename = f"{data_type}_{data_id}.json"
        file_path = storage_dir / filename
        
        # Write the data
        with open(file_path, 'w') as f:
            f.write(json_data)
        
        logger.info(f"Successfully saved to local storage: {file_path}")
        
        return {
            'success': True,
            'storage': 'local',
            'id': data_id,
            'filename': filename,
            'file_path': str(file_path),
            'timestamp': timestamp
        }
    except Exception as e:
        logger.error(f"Error saving to local storage: {e}")
        return {
            'success': False,
            'storage': 'none',
            'error': str(e)
        }

def get_from_filebase(data_id, data_type='crawl_results'):
    """
    Retrieve data from Filebase (or local storage)
    
    Args:
        data_id: The ID of the data to retrieve
        data_type: Type of data
        
    Returns:
        dict: The retrieved data or None if not found
    """
    filename = f"{data_type}_{data_id}.json"
    
    # If Filebase is configured, try to get from there first
    if is_filebase_configured():
        try:
            logger.info(f"Retrieving data from Filebase: {data_type}, {data_id}")
            
            # Use boto3 to download from Filebase (S3-compatible API)
            try:
                # Create an S3 client with Filebase endpoint
                s3_client = boto3.client(
                    's3',
                    endpoint_url=FILEBASE_ENDPOINT,
                    aws_access_key_id=FILEBASE_ACCESS_KEY,
                    aws_secret_access_key=FILEBASE_SECRET_KEY,
                    config=Config(signature_version='s3v4')
                )
                
                # Download the file
                response = s3_client.get_object(
                    Bucket=FILEBASE_BUCKET,
                    Key=filename
                )
                
                # Read the content
                content = response['Body'].read().decode('utf-8')
                
                logger.info(f"Successfully retrieved from Filebase: {filename}")
                return json.loads(content)
            else:
                logger.warning(f"Failed to retrieve from Filebase: {response.status_code}")
                # Fall back to local storage
                return _get_from_local_storage(data_id, data_type)
                
        except Exception as e:
            logger.error(f"Error retrieving from Filebase: {e}")
            # Fall back to local storage
            return _get_from_local_storage(data_id, data_type)
    else:
        # Use local storage
        logger.info(f"Filebase not configured, retrieving from local storage: {data_type}, {data_id}")
        return _get_from_local_storage(data_id, data_type)

def _get_from_local_storage(data_id, data_type):
    """Retrieve data from local storage"""
    try:
        # Create the file path
        filename = f"{data_type}_{data_id}.json"
        file_path = LOCAL_STORAGE_DIR / data_type / filename
        
        # Check if the file exists
        if not file_path.exists():
            logger.warning(f"File not found in local storage: {file_path}")
            return None
        
        # Read the data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Successfully retrieved from local storage: {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error retrieving from local storage: {e}")
        return None

def list_filebase_data(data_type='crawl_results', limit=100):
    """
    List data stored in Filebase (or local storage)
    
    Args:
        data_type: Type of data to list
        limit: Maximum number of items to return
        
    Returns:
        list: List of data items with metadata
    """
    # If Filebase is configured, list from there
    if is_filebase_configured():
        try:
            logger.info(f"Listing data from Filebase: {data_type}")
            
            # Use boto3 to list objects from Filebase (S3-compatible API)
            try:
                # Create an S3 client with Filebase endpoint
                s3_client = boto3.client(
                    's3',
                    endpoint_url=FILEBASE_ENDPOINT,
                    aws_access_key_id=FILEBASE_ACCESS_KEY,
                    aws_secret_access_key=FILEBASE_SECRET_KEY,
                    config=Config(signature_version='s3v4')
                )
                
                # List objects with the prefix
                response = s3_client.list_objects_v2(
                    Bucket=FILEBASE_BUCKET,
                    Prefix=f"{data_type}_",
                    MaxKeys=limit
                )
                
                # Extract the object keys
                items = []
                if 'Contents' in response:
                    for obj in response['Contents']:
                        key = obj['Key']
                        last_modified = obj['LastModified'].isoformat()
                        size = obj['Size']
                        
                        # Extract the data_id from the key
                        data_id = key.split('_', 1)[1].split('.', 1)[0]
                        
                        items.append({
                            'id': data_id,
                            'filename': key,
                            'last_modified': last_modified,
                            'size': size,
                            'storage': 'filebase',
                            'url': f"{FILEBASE_ENDPOINT}/{FILEBASE_BUCKET}/{key}"
                        })
                
                logger.info(f"Successfully listed {len(items)} items from Filebase")
                return items
            else:
                logger.warning(f"Failed to list from Filebase: {response.status_code}")
                # Fall back to local storage
                return _list_local_storage(data_type, limit)
                
        except Exception as e:
            logger.error(f"Error listing from Filebase: {e}")
            # Fall back to local storage
            return _list_local_storage(data_type, limit)
    else:
        # Use local storage
        logger.info(f"Filebase not configured, listing from local storage: {data_type}")
        return _list_local_storage(data_type, limit)

def _list_local_storage(data_type, limit=100):
    """List data stored in local storage"""
    try:
        # Create the directory path
        storage_dir = LOCAL_STORAGE_DIR / data_type
        
        # Check if the directory exists
        if not storage_dir.exists():
            logger.warning(f"Directory not found in local storage: {storage_dir}")
            return []
        
        # List files
        items = []
        for file_path in sorted(storage_dir.glob(f"{data_type}_*.json"), key=os.path.getmtime, reverse=True)[:limit]:
            # Extract the data_id from the filename
            filename = file_path.name
            data_id = filename.split('_', 1)[1].split('.', 1)[0]
            
            # Get file stats
            stats = file_path.stat()
            
            items.append({
                'id': data_id,
                'filename': filename,
                'last_modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.st_mtime)),
                'size': stats.st_size,
                'storage': 'local',
                'file_path': str(file_path)
            })
        
        logger.info(f"Successfully listed {len(items)} items from local storage")
        return items
    except Exception as e:
        logger.error(f"Error listing from local storage: {e}")
        return []

def delete_from_filebase(data_id, data_type='crawl_results'):
    """
    Delete data from Filebase (or local storage)
    
    Args:
        data_id: The ID of the data to delete
        data_type: Type of data
        
    Returns:
        bool: True if successful, False otherwise
    """
    filename = f"{data_type}_{data_id}.json"
    
    # If Filebase is configured, delete from there
    if is_filebase_configured():
        try:
            logger.info(f"Deleting data from Filebase: {data_type}, {data_id}")
            
            # Use boto3 to delete from Filebase (S3-compatible API)
            try:
                # Create an S3 client with Filebase endpoint
                s3_client = boto3.client(
                    's3',
                    endpoint_url=FILEBASE_ENDPOINT,
                    aws_access_key_id=FILEBASE_ACCESS_KEY,
                    aws_secret_access_key=FILEBASE_SECRET_KEY,
                    config=Config(signature_version='s3v4')
                )
                
                # Delete the object
                response = s3_client.delete_object(
                    Bucket=FILEBASE_BUCKET,
                    Key=filename
                )
                
                logger.info(f"Successfully deleted from Filebase: {filename}")
                return True
            else:
                logger.warning(f"Failed to delete from Filebase: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting from Filebase: {e}")
            return False
    
    # Also try to delete from local storage
    return _delete_from_local_storage(data_id, data_type)

def _delete_from_local_storage(data_id, data_type):
    """Delete data from local storage"""
    try:
        # Create the file path
        filename = f"{data_type}_{data_id}.json"
        file_path = LOCAL_STORAGE_DIR / data_type / filename
        
        # Check if the file exists
        if not file_path.exists():
            logger.warning(f"File not found in local storage: {file_path}")
            return False
        
        # Delete the file
        file_path.unlink()
        
        logger.info(f"Successfully deleted from local storage: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error deleting from local storage: {e}")
        return False

def _get_filebase_auth(access_key, secret_key):
    """Generate the Authorization header for Filebase S3-compatible API"""
    try:
        # Try to use boto3 for proper AWS signature if available
        import boto3
        from botocore.auth import SigV4Auth
        from botocore.awsrequest import AWSRequest
        import datetime
        
        request = AWSRequest(
            method='GET',
            url=FILEBASE_ENDPOINT,
            data=''
        )
        
        credentials = boto3.Session().get_credentials()
        if not credentials:
            # Create credentials object manually
            from botocore.credentials import Credentials
            credentials = Credentials(access_key, secret_key)
        
        auth = SigV4Auth(credentials, 's3', 'us-east-1')
        auth.add_auth(request)
        
        return request.headers['Authorization']
    except ImportError:
        # Fall back to basic auth if boto3 is not available
        logger.warning("boto3 not available, falling back to basic auth which may not work with all S3 providers")
        credentials = f"{access_key}:{secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"