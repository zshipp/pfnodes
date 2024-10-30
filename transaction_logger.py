import csv
from datetime import datetime
import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import TransactionEntry

# Define the log file name
LOG_FILE = 'transaction_log.csv'
XRP_RPC_URL = "https://s2.ripple.com:51234"  # XRPL public endpoint

# Initialize XRPL client
client = JsonRpcClient(XRP_RPC_URL)

# Function to add a transaction with blockchain details
def add_transaction(tx_hash):
    # Fetch transaction details from the XRP ledger
    tx_request = TransactionEntry(transaction=tx_hash)
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

# Function to calculate the total contributions and per-member totals
def calculate_total_contributions():
    total = 0
    member_totals = {}  # Dictionary for individual member totals
    church_total = 0  # Total for the church (Receiver address)

    with open(LOG_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            amount = float(row["Amount"])
            total += amount

            sender = row["Sender"]
            receiver = row["Receiver"]

            # Debug prints to check each row's data
            print(f"Processing row: Sender={sender}, Receiver={receiver}, Amount={amount}")

            # Track individual sender contributions
            if sender in member_totals:
                member_totals[sender] += amount
            else:
                member_totals[sender] = amount

            # Track contributions received by the church
            if receiver == "churchAddr":  # Replace "churchAddr" with the actual church address
                church_total += amount

            # Debug prints to show current totals after processing each row
            print(f"Current member_totals: {member_totals}")
            print(f"Current church_total: {church_total}")

    # Display totals
    print(f"Total Contributions: {total}")
    print("Member Contributions:")
    for member, amount in member_totals.items():
        print(f"{member}: {amount}")
    print(f"Church Total Contributions: {church_total}")

    return total, member_totals, church_total

# Example usage
if __name__ == "__main__":
   
    calculate_total_contributions()
