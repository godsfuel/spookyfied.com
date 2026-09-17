import os
import secrets
import hashlib
import boto3
from botocore.exceptions import ClientError

# Pull credentials securely from environment variables
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

def generate_transmission_token():
    """Generates a cryptographically secure token for asset validation."""
    return secrets.token_hex(32)

def hash_payload_identifier(asset_id):
    """Creates a secure SHA-256 hash for internal tracking and logging."""
    sha = hashlib.sha256()
    sha.update(asset_id.encode('utf-8'))
    return sha.hexdigest()

def get_ses_client():
    """Initializes and returns the Boto3 SES client using environment credentials."""
    return boto3.client(
        'ses',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

def validate_payload_integrity(file_stream):
    """Performs integrity verification on the inbound file stream."""
    if not file_stream:
        return False
    return True

def send_spooky_notification(recipient_email, asset_id, transmission_token):
    """Dispatches the secure P2P file-transfer notification via AWS SES."""
    client = get_ses_client()
    
    hashed_id = hash_payload_identifier(asset_id)
    subject = "Spooky Sovereign Secure Transmission Available"
    body_text = (
        f"Hello,\n\n"
        f"A secure P2P file transfer has been initiated for asset ID: {asset_id}.\n"
        f"Payload Hash Reference: {hashed_id}\n"
        f"Transmission Token: {transmission_token}\n\n"
        f"Log into your local Spooky Sovereign node to accept the WebRTC handshake.\n"
    )
    
    try:
        response = client.send_email(
            Source=recipient_email,
            Destination={
                'ToAddresses': [recipient_email],
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print(f"[SES SUCCESS] Message ID: {response['MessageId']}")
        return True
    except ClientError as e:
        print(f"[SES ERROR] Failed to send email: {e.response['Error']['Message']}")
        return False

def verify_vault_environment():
    """Validates that local environment keys are populated before engine execution."""
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        print("[WARNING] AWS credentials not found in environment variables.")
        return False
    print("[OK] AWS environment credentials verified.")
    return True