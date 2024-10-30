import csv
import matplotlib.pyplot as plt
from datetime import datetime
import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import TransactionEntry

# Define the log file name and XRPL public endpoint
LOG_FILE = 'transaction_log.csv'
XRP_RPC_URL = "https://s2.ripple.com:51234"

# Initialize XRPL client
client = JsonRpcClient(XRP_RPC_URL)

# Function to add a transaction with blockchain details
def add_transaction(tx_hash):
    tx_request = TransactionEntry(transaction=tx_hash)
    tx_response = client.request(tx_request)

    if tx_response.is_successful():
        tx_result = tx_response.result
        timestamp = datetime.now().isoformat()
        sender = tx_result['Account']
        receiver = tx_result['Destination']
        amount = tx_result.get('Amount')
        memo = None
        if 'Memos' in tx_result:
            memo = bytes.fromhex(tx_result['Memos'][0]['Memo']['MemoData']).decode('utf-8')

        # Append transaction data to CSV
        with open(LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, tx_hash, sender, receiver, amount, memo])
        
        print(f"Transaction logged: {timestamp}, {tx_hash}, {sender}, {receiver}, {amount}, {memo}")
    else:
        print(f"Failed to retrieve transaction {tx_hash}")

# Function to initialize log file with headers
def initialize_log():
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Transaction Hash", "Sender", "Receiver", "Amount", "Memo"])
    print("Log initialized with headers.")

# Function to calculate total contributions and individual totals
def calculate_total_contributions():
    total = 0
    member_totals = {}
    church_total = 0

    with open(LOG_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            amount = float(row["Amount"])
            total += amount
            sender = row["Sender"]
            receiver = row["Receiver"]

            # Track individual contributions
            if sender in member_totals:
                member_totals[sender] += amount
            else:
                member_totals[sender] = amount

            if receiver == "churchAddr":  # Replace with the actual church address
                church_total += amount

    print(f"Total Contributions: {total}")
    print("Member Contributions:")
    for member, amount in member_totals.items():
        print(f"{member}: {amount}")
    print(f"Church Total Contributions: {church_total}")

    return total, member_totals, church_total

# Function to summarize and visualize contributions for a specific member
def calculate_member_contributions(member_id):
    total = 0
    ritual_counts = {}
    total_contributions = 0
    contribution_count = 0

    with open(LOG_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Sender"] == member_id:
                amount = float(row["Amount"])
                total += amount
                contribution_count += 1
                total_contributions += amount
                ritual_type = row["Memo"]
                ritual_counts[ritual_type] = ritual_counts.get(ritual_type, 0) + 1

    return {
        "total_contributions": total,
        "contribution_count": contribution_count,
        "ritual_counts": ritual_counts
    }

# New combined visual summary function
def create_visual_summary(member_id):
    data = calculate_member_contributions(member_id)
    total, member_totals, church_total = calculate_total_contributions()
    
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # Total Contributions per Member
    axs[0, 0].bar(member_totals.keys(), member_totals.values())
    axs[0, 0].set_title('Total Contributions per Member')
    axs[0, 0].set_xlabel('Member ID')
    axs[0, 0].set_ylabel('Total Amount')

    # Contributions to the Church
    axs[0, 1].bar(['Church Total'], [church_total])
    axs[0, 1].set_title('Total Contributions to Church')
    axs[0, 1].set_ylabel('Total Amount')

    # Ritual Distribution per Member
    axs[1, 0].bar(data["ritual_counts"].keys(), data["ritual_counts"].values())
    axs[1, 0].set_title(f'Ritual Type Distribution for {member_id}')
    axs[1, 0].set_xlabel('Ritual Type')
    axs[1, 0].set_ylabel('Count')

    # Number of Contributions per Member
    axs[1, 1].bar(["Total Rituals"], [data["contribution_count"]])
    axs[1, 1].set_title(f'Total Rituals for {member_id}')
    axs[1, 1].set_ylabel("Number of Rituals")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # initialize_log()  # Uncomment if initializing
    calculate_total_contributions()
    create_visual_summary("senderAddr")  # Replaced with a specific member ID for testing. This will need to be called to see an indiviuals memmbers visual summary
