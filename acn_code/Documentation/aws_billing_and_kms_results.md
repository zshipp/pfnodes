Documenting the AWS Billing Alert Configuration:
AWS Billing Alert: Created a Zero-Spend Budget in the AWS Budgets section.
Alert Threshold: The alert was set to notify when spending exceeds $0.01 (this is for AWS Free Tier usage).
Notification: Configured an email notification to be sent when the budget threshold is exceeded.
Documenting KMS Test Results:
KMS Function Tested: Tested the AWS KMS (Key Management Service) functions for encryption and decryption using the AWS CLI.
Encryption: Used the command:

bash
Copy code
aws kms encrypt --key-id <YourKMSKeyID> --plaintext "test_secret" --output text --query CiphertextBlob
This command encrypts the plaintext string "test_secret" using your KMS key.

Decryption: After encryption, used the following command to decrypt the data:

bash
Copy code
aws kms decrypt --ciphertext-blob <CiphertextBlob> --output text --query Plaintext
This command successfully decrypted the encrypted data, and the output was logged and matched the original plaintext string "test_secret".

Verification: Verified that both encryption and decryption worked as expected by comparing the decrypted data to the original plaintext value. The KMS function was confirmed as working correctly.

