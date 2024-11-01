import os
from dotenv import load_dotenv

class PasswordMapLoader:
    def __init__(self, env_file_path=".env"):
        # Load environment variables from the specified .env file
        load_dotenv(env_file_path)
    
    def get_password(self, key):
        # Retrieve password or other sensitive info from environment variables
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Environment variable '{key}' not found.")
        return value
