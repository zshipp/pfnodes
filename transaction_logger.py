import csv
from datetime import datetime
import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import Transaction

# Define the log file name
LOG_FILE = 'transaction_log.csv'
XRP_RPC_URL = "https://s2.ripple.com:51234"  # XRPL public endpoint

# Initialize XRPL client
client = JsonRpcClient(XRP_RPC_URL)

# Function to add a transaction with blockchain details
def add_transaction(tx_hash):
    # Fetch transaction details from the XRP ledger
    tx_request = Transaction(transaction=tx_hash)
    tx_response = client.request(tx_request)
    
    if tx_response.is_successful():
        tx_result = tx_response.result
        timestamp = datetime.now().isoformat()  # Local timestamp
        sender = tx_result['Account']
        receiver = tx_result['Destination']
        amount = tx_result.get('Amount')
        memo = None
        if 'Memos' in tx_result:
            # Decode the memo from hex if present
            memo = bytes.fromhex(tx_result['Memos'][0]['Memo']['MemoData']).decode('utf-8')
        
        # Append the transaction data to the CSV file
        with open(LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, tx_hash, sender, receiver, amount, memo])
        
        print(f"Transaction logged: {timestamp}, {tx_hash}, {sender}, {receiver}, {amount}, {memo}")
    else:
        print(f"Failed to retrieve transaction {tx_hash}")

# Function to initialize the log file with headers
def initialize_log():
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Transaction Hash", "Sender", "Receiver", "Amount", "Memo"])
    print("Log initialized with headers.")

# Example usage
if __name__ == "__main__":
    initialize_log()  # Run once to set up headers
    # Replace with an actual transaction hash from XRP ledger for testing
    add_transaction('ENTER_TRANSACTION_HASH_HERE')  
