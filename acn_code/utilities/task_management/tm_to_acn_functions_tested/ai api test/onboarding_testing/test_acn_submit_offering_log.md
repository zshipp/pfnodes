Starting ACN Command Flow Test...

=== Testing ACN Command Flow ===
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

1. Test /status before any interaction:
Deferring response for user test_pilgrim_1
Wallet initialized with classic address rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf

Discord Response: Discord ID: test_pilgrim_1
Wallet registered: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
Initial greeting: Pending
Ready for main offering: No - Use /offering first
Initial Status Response: Discord ID: test_pilgrim_1
Wallet registered: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
Initial greeting: Pending
Ready for main offering: No - Use /offering first

2. Test /submit_offering before initial greeting:
Deferring response for user test_pilgrim_1

Processing main offering transaction...
Wallet initialized with classic address rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf

Initiating transaction of 100 PFT
From: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
To: rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd

Checking PFT balance for rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
No PFT trust line found

ERROR: Transaction failed: Insufficient PFT balance for sending 100 PFT
Error processing offering: Transaction failed: Insufficient PFT balance for sending 100 PFT

Discord Response: The Church's mechanisms falter: Error processing offering: Transaction failed: Insufficient PFT balance for sending 100 PFT
Early Submit Response: The Church's mechanisms falter: Error processing offering: Transaction failed: Insufficient PFT balance for sending 100 PFT

3. Test initial /offering command:
Deferring response for user test_pilgrim_1

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
Initial Offering Response: The Church's mechanisms falter: Error processing offering request: Transaction failed: Insufficient PFT balance for sending 1 PFT

4. Check status after initial offering:
Deferring response for user test_pilgrim_1
Wallet initialized with classic address rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf

Discord Response: Discord ID: test_pilgrim_1
Wallet registered: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
Initial greeting: Pending
Ready for main offering: No - Use /offering first
Mid-Flow Status Response: Discord ID: test_pilgrim_1
Wallet registered: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
Initial greeting: Pending
Ready for main offering: No - Use /offering first

5. Test main /submit_offering command:
Deferring response for user test_pilgrim_1

Processing main offering transaction...
Wallet initialized with classic address rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf

Initiating transaction of 500 PFT
From: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
To: rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd

Checking PFT balance for rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
No PFT trust line found

ERROR: Transaction failed: Insufficient PFT balance for sending 500 PFT
Error processing offering: Transaction failed: Insufficient PFT balance for sending 500 PFT

Discord Response: The Church's mechanisms falter: Error processing offering: Transaction failed: Insufficient PFT balance for sending 500 PFT
Main Offering Response: The Church's mechanisms falter: Error processing offering: Transaction failed: Insufficient PFT balance for sending 500 PFT

6. Try /offering again (should be blocked):
Deferring response for user test_pilgrim_1

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
Repeat Offering Response: The Church's mechanisms falter: Error processing offering request: Transaction failed: Insufficient PFT balance for sending 1 PFT

7. Final status check:
Deferring response for user test_pilgrim_1
Wallet initialized with classic address rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf

Discord Response: Discord ID: test_pilgrim_1
Wallet registered: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
Initial greeting: Pending
Ready for main offering: No - Use /offering first
Final Status Response: Discord ID: test_pilgrim_1
Wallet registered: rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf
Initial greeting: Pending
Ready for main offering: No - Use /offering first

Database Interaction Logs:
M:\pft\PFT Documentation\code\Accelerando Church Node\acn_code\utilities\task_management\tm_to_acn_functions_tested\ai api test\onboarding_testing\db_manager.py:125: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
  return pd.read_sql(query, conn, params=[discord_user_id])

Full interaction history:

Interaction 1:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 13:02:20.683173
--------------------------------------------------

Interaction 2:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 13:02:20.427126
--------------------------------------------------

Interaction 3:
Type: submit_offering
Amount: 500.0
Success: True
Timestamp: 2024-11-12 13:02:19.212517
--------------------------------------------------

Interaction 4:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 13:02:17.907271
--------------------------------------------------

Interaction 5:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 13:02:17.689390
--------------------------------------------------

Interaction 6:
Type: submit_offering
Amount: 100.0
Success: True
Timestamp: 2024-11-12 13:02:16.255847
--------------------------------------------------

Interaction 7:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 13:02:14.920192
--------------------------------------------------

Interaction 8:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:56:12.531754
--------------------------------------------------

Interaction 9:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 12:56:12.393087
--------------------------------------------------

Interaction 10:
Type: submit_offering
Amount: nan
Success: False
Timestamp: 2024-11-12 12:56:11.220527
--------------------------------------------------

Interaction 11:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:56:11.023597
--------------------------------------------------

Interaction 12:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 12:56:10.781337
--------------------------------------------------

Interaction 13:
Type: submit_offering
Amount: nan
Success: False
Timestamp: 2024-11-12 12:56:09.498046
--------------------------------------------------

Interaction 14:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:56:09.418447
--------------------------------------------------

Interaction 15:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:48:59.098246
--------------------------------------------------

Interaction 16:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 12:48:58.851234
--------------------------------------------------

Interaction 17:
Type: submit_offering
Amount: nan
Success: False
Timestamp: 2024-11-12 12:48:57.688015
--------------------------------------------------

Interaction 18:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:48:57.606165
--------------------------------------------------

Interaction 19:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 12:48:57.358293
--------------------------------------------------

Interaction 20:
Type: submit_offering
Amount: nan
Success: False
Timestamp: 2024-11-12 12:48:52.641254
--------------------------------------------------

Interaction 21:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:48:52.459697
--------------------------------------------------

Interaction 22:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:43:36.069794
--------------------------------------------------

Interaction 23:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 12:43:35.828616
--------------------------------------------------

Interaction 24:
Type: submit_offering
Amount: nan
Success: False
Timestamp: 2024-11-12 12:43:34.644898
--------------------------------------------------

Interaction 25:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:43:34.561720
--------------------------------------------------

Interaction 26:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 12:43:34.424899
--------------------------------------------------

Interaction 27:
Type: submit_offering
Amount: nan
Success: False
Timestamp: 2024-11-12 12:43:33.244926
--------------------------------------------------

Interaction 28:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:43:33.162339
--------------------------------------------------

Interaction 29:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:38:44.876833
--------------------------------------------------

Interaction 30:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 12:38:44.636442
--------------------------------------------------

Interaction 31:
Type: submit_offering
Amount: nan
Success: False
Timestamp: 2024-11-12 12:38:43.479287
--------------------------------------------------

Interaction 32:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:38:43.290052
--------------------------------------------------

Interaction 33:
Type: offering
Amount: 1.0
Success: True
Timestamp: 2024-11-12 12:38:43.036961
--------------------------------------------------

Interaction 34:
Type: submit_offering
Amount: nan
Success: False
Timestamp: 2024-11-12 12:38:41.765546
--------------------------------------------------

Interaction 35:
Type: status
Amount: nan
Success: True
Timestamp: 2024-11-12 12:38:41.687258
--------------------------------------------------

Interaction 36:
Type: offering
Amount: nan
Success: True
Timestamp: 2024-11-12 08:48:18.800334
--------------------------------------------------

Interaction 37:
Type: offering
Amount: nan
Success: True
Timestamp: 2024-11-12 08:45:35.455221
--------------------------------------------------

Interaction 38:
Type: offering
Amount: nan
Success: False
Timestamp: 2024-11-12 08:41:15.091028
--------------------------------------------------

Interaction 39:
Type: offering
Amount: nan
Success: False
Timestamp: 2024-11-12 08:39:52.269540
--------------------------------------------------