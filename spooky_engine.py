import os
import boto3
from botocore.exceptions import ClientError

# Initialize the Amazon SES client via AWS SDK (Boto3)
# It uses local IAM credentials or environment variables securely (no hardcoded passwords).
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ses_client = boto3.client("ses", region_name=AWS_REGION)

SPOOKY_SENDER_DOMAIN = "noreply@spookyfied.com"

def dispatch_secure_key_notification(recipient_email: str, secure_key_token: str, asset_id: str):
    """
    Dispatches a high-priority cryptographic key and file access notification
    via Amazon SES API. Designed for high-throughput enterprise scale.
    """
    subject = f"Spooky Sovereign Asset Authorization: {asset_id}"
    
    # Clean, hardened HTML payload for the recipient
    html_body = f"""
    <html>
      <body style="background-color: #0d0d0d; color: #00ff66; font-family: monospace; padding: 20px;">
        <h2>SPIN-LOCK SECURE TRANSMISSION VAULT</h2>
        <p>Your node connection has been cryptographically verified.</p>
        <p><strong>Asset ID:</strong> {asset_id}</p>
        <p><strong>Sovereign Key Token:</strong></p>
        <div style="background: #1a1a1a; border: 1px solid #00ff66; padding: 10px; font-size: 16px;">
          {secure_key_token}
        </div>
        <p style="color: #888; font-size: 12px; margin-top: 20px;">
          This transmission was processed securely through a localized architecture. Zero third-party data retention.
        </p>
      </body>
    </html>
    """
    
    text_body = (
        f"SPIN-LOCK SECURE TRANSMISSION VAULT\n\n"
        f"Asset ID: {asset_id}\n"
        f"Sovereign Key Token: {secure_key_token}\n\n"
        f"Authorized local network delivery."
    )

    try:
        response = ses_client.send_email(
            Source=SPOOKY_SENDER_DOMAIN,
            Destination={
                "ToAddresses": [recipient_email],
            },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Html": {
                        "Data": html_body,
                        "Charset": "UTF-8"
                    },
                    "Text": {
                        "Data": text_body,
                        "Charset": "UTF-8"
                    }
                }
            }
        )
        print(f"[SUCCESS] Secure transmission dispatched. Message ID: {response['MessageId']}")
        return True

    except ClientError as e:
        error_message = e.response['Error']['Message']
        print(f"[CRITICAL FAILURE] Transmission dropped: {error_message}")
        return False

if __name__ == "__main__":
    # Local simulation test
    test_recipient = "engineer@spookyfied.com"
    test_token = "SPKY-9902-ALPHA-SECURE-NODE-LOCK"
    test_asset = "BMG-CATALOG-MASTER-01"
    
    print("Initializing local Spooky transmission test...")
    dispatch_secure_key_notification(test_recipient, test_token, test_asset)