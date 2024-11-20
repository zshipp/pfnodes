1. Transferred ACN Bot Code to EC2 Instance
The ACN bot’s core code was transferred to the EC2 instance using Git. The repository was cloned to the instance to ensure that the latest code was used for the environment setup.

2. Set Up Python Environment
A Python 3 virtual environment was created on the EC2 instance to isolate dependencies and avoid conflicts with the system's Python installation.
Command used to create the virtual environment:
bash
Copy code
python3 -m venv acn_bot_env


The virtual environment was activated:
bash
Copy code
source acn_bot_env/bin/activate



3. Installed Necessary Dependencies
The required Python packages for the ACN bot were installed via the requirements.txt file.
The dependencies were successfully installed using the following command:
bash
Copy code
pip install -r /path/to/requirements.txt



4. Configured Environment Variables
Created a .env file in the project directory with the following environment variables:
AWS_REGION
KMS_KEY_ID
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
Plus other ENVS - discord, postgres, wallets
These environment variables were loaded using python-dotenv to ensure the bot can interact with AWS services securely.

5. Tested KMS Encryption on EC2 Instance
The KMS encryption was tested on the EC2 instance to ensure the bot can encrypt and decrypt data using the AWS KMS service.
The test was conducted using the kms_encryption.py and test_kms_encryption.py files.
The encryption and decryption process was successful, confirming that the EC2 instance has the correct permissions to access KMS.
The output of the test was as follows:
(acn_onboarding_bot_env) [ec2-user@ip-172-31-14-165 onboarding_testing]$ python test_kms_encryption.py
DEBUG (kms_encryption.py): AWS_REGION = ap-southeast-2
DEBUG: Environment variables loaded.
DEBUG: Retrieved value for AWS_REGION.
DEBUG (test_kms_encryption.py): AWS_REGION loaded = ap-southeast-2
DEBUG: boto3 KMS client initialized.
DEBUG: Starting KMS Encryption/Decryption Test...
DEBUG: Encrypting data...
DEBUG: Starting encryption...
DEBUG: Encryption completed.
DEBUG: Data encrypted successfully.
DEBUG: Decrypting data...
DEBUG: Starting decryption...
DEBUG: Decryption completed.
DEBUG: Data decrypted successfully.
DEBUG: Validating decrypted data...
DEBUG: Test passed!
(acn_onboarding_bot_env) [ec2-user@ip-172-31-14-165 onboarding_testing]$




6. Validated Bot Connectivity
The bot was checked for connectivity, ensuring it could connect to external services such as Discord or other APIs it uses.
The bot is running and responding as expected, confirming successful connectivity.
