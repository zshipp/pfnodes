# Initialize the transaction log file with headers
import csv

LOG_FILE = 'transaction_log.csv'

def initialize_log():
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Transaction Hash", "Sender", "Receiver", "Amount", "Memo"])
    print("Log initialized with headers.")

# Run this once to initialize
initialize_log()
