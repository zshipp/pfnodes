import csv
from datetime import datetime

def log_transaction(transaction_hash, sender, receiver, member_id, amount, ritual_detail="", memo=""):
    with open("transaction_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), transaction_hash, sender, receiver, member_id, amount, ritual_detail, memo])
    print("Transaction logged successfully.")
