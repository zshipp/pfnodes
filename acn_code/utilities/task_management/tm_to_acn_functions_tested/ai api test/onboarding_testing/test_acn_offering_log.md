Starting ACN Offering Command Test...

=== Testing ACN Offering Command ===
Password map loaded
Connected to XRPL mainnet at https://xrplcluster.com
Wallet initialized with classic address rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd
Initialized accelerandochurch node wallet: rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd

Checking PFT balance for rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd
Current PFT balance: 111.0
Balance sufficient
PFT trust line verified
Generic utilities initialized
ACN LLM Interface Initialized with GPT-4 model.
LLM interface initialized
Character prompts loaded

1. Testing wallet creation and initial offering:

Attempting to store wallet...
Wallet initialized with classic address rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
Wallet stored/updated for test_pilgrim_1
Wallet stored successfully: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf

Testing offering command...

Processing initial offering request...
Wallet initialized with classic address rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
Wallet initialized with classic address rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
Wallet stored/updated for test_pilgrim_1

Initiating transaction of 1 PFT
From: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
To: rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd

Checking PFT balance for rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
No PFT trust line found

ERROR: Transaction failed: Insufficient PFT balance for sending 1 PFT
Error processing offering request: Transaction failed: Insufficient PFT balance for sending 1 PFT

Discord Response: The Church's mechanisms falter: Error processing offering request: Transaction failed: Insufficient PFT balance for sending 1 PFT
Command completed. Response: None
M:\pft\PFT Documentation\code\Accelerando Church Node\acn_code\utilities\task_management\tm_to_acn_functions_tested\ai api test\onboarding_testing\db_manager.py:125: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  return pd.read_sql(query, conn, params=[discord_user_id])

Database Logs:
  interaction_type amount  success                                   response_message                  timestamp
0         offering   None     True  The Church's mechanisms falter: Error processi... 2024-11-12 08:48:18.800334
1         offering   None     True  The Church's mechanisms falter: Error processi... 2024-11-12 08:45:35.455221
2         offering   None    False  Error during offering: ACNode.process_ac_offer... 2024-11-12 08:41:15.091028
3         offering   None    False  Error during offering: ACNode.process_ac_offer... 2024-11-12 08:39:52.269540

Detailed log entry:
interaction_type: offering
amount: None
success: True
response_message: The Church's mechanisms falter: Error processing offering request: Transaction failed: Insufficient PFT balance for sending 1 PFT
timestamp: 2024-11-12 08:48:18.800334