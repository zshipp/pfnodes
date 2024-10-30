import csv
from datetime import datetime

# Logs a new transaction
def log_transaction(transaction_hash, sender, receiver, member_id, amount, ritual_detail="", memo=""):
    with open("transaction_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), transaction_hash, sender, receiver, member_id, amount, ritual_detail, memo])
    print("Transaction logged successfully.")

# Calculates the total contributions from the CSV log
def calculate_total_contributions():
    total = 0
    with open("transaction_log.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            total += float(row["Amount"])
    print(f"Total Contributions: {total}")
    return total

# Place this at the end of log_transaction.py
if __name__ == "__main__":
    calculate_total_contributions()
