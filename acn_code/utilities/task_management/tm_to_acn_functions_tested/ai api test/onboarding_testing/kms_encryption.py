import boto3
import os
from dotenv import load_dotenv

# Explicitly load environment variables
load_dotenv()

# Debug: Check if environment variables are loaded correctly
region = os.getenv('AWS_REGION')
kms_key_id = os.getenv('KMS_KEY_ID')
print(f"DEBUG (kms_encryption.py): AWS_REGION = {region}")  # Removed kms_key_id from output

# Initialize the KMS client using environment variables
if not region:
    raise ValueError("AWS_REGION is not set. Please check your .env file.")
if not kms_key_id:
    raise ValueError("KMS_KEY_ID is not set. Please check your .env file.")

kms_client = boto3.client('kms', region_name=region)

def encrypt_data(data):
    """
    Encrypts plaintext data using AWS KMS.
    
    Args:
        data (str): The plaintext string to encrypt.
    
    Returns:
        bytes: Encrypted data (CiphertextBlob).
    """
    print("DEBUG: Starting encryption...")
    response = kms_client.encrypt(
        KeyId=kms_key_id,
        Plaintext=data.encode('utf-8')
    )
    print("DEBUG: Encryption completed.")
    return response['CiphertextBlob']

def decrypt_data(ciphertext):
    """
    Decrypts KMS-encrypted data back to plaintext.
    
    Args:
        ciphertext (bytes): Encrypted data (CiphertextBlob).
    
    Returns:
        str: Decrypted plaintext.
    """
    print("DEBUG: Starting decryption...")
    response = kms_client.decrypt(
        CiphertextBlob=ciphertext
    )
    print("DEBUG: Decryption completed.")
    return response['Plaintext'].decode('utf-8')
