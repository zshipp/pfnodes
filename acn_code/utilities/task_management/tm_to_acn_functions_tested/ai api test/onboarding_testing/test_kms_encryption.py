import boto3
from password_map_loader import PasswordMapLoader
from kms_encryption import encrypt_data, decrypt_data

# Initialize PasswordMapLoader
loader = PasswordMapLoader()

# Debugging: Confirm AWS_REGION is loaded correctly
region = loader.get_password("AWS_REGION")  # Load region before using it
print(f"DEBUG (test_kms_encryption.py): AWS_REGION loaded = {region}")

# Initialize boto3 client manually (if needed for debugging)
kms_client = boto3.client('kms', region_name=region)
print("DEBUG: boto3 KMS client initialized.")

# Test data
test_data = "my_secret_wallet_seed"
print("DEBUG: Starting KMS Encryption/Decryption Test...")

# Step 1: Encrypt the data
try:
    print("DEBUG: Encrypting data...")
    encrypted = encrypt_data(test_data)
    print("DEBUG: Data encrypted successfully.")
except Exception as e:
    print(f"ERROR: Encryption failed - {e}")
    raise

# Step 2: Decrypt the data
try:
    print("DEBUG: Decrypting data...")
    decrypted = decrypt_data(encrypted)
    print("DEBUG: Data decrypted successfully.")
except Exception as e:
    print(f"ERROR: Decryption failed - {e}")
    raise

# Step 3: Validate the result
try:
    print("DEBUG: Validating decrypted data...")
    assert decrypted == test_data, "Decryption failed! The decrypted data does not match the original."
    print("DEBUG: Test passed!")
except AssertionError as e:
    print(f"ERROR: Validation failed - {e}")
    raise
