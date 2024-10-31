import csv
from datetime import datetime

# Paths to the log files
TRANSACTION_LOG = 'transaction_log.csv'
RITUAL_LOG = 'ritual_log.csv'
TITHE_LOG = 'tithe_log.csv'
AUDIT_REPORT = 'audit_report.csv'

def load_log(file_path):
    """Load CSV data from the specified file."""
    data = []
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def find_discrepancies(transaction_log, ritual_log, tithe_log):
    """Identify discrepancies between the logs."""
    discrepancies = []

    # Cross-check entries in each log
    for t_log in transaction_log:
        t_timestamp = t_log['Timestamp']
        t_member_id = t_log['Sender']
        t_amount = float(t_log['Amount'])

        # Check for matching entries in ritual log
        ritual_match = any(
            r['Timestamp'] == t_timestamp and
            r['Member ID'] == t_member_id and
            float(r['Amount']) == t_amount
            for r in ritual_log
        )

        # Check for matching entries in tithe log
        tithe_match = any(
            d['Timestamp'] == t_timestamp and
            d['Member ID'] == t_member_id and
            float(d['Amount']) == t_amount
            for d in tithe_log
        )

        if not ritual_match or not tithe_match:
            discrepancies.append({
                'Timestamp': t_timestamp,
                'Member ID': t_member_id,
                'Amount': t_amount,
                'Ritual Match': ritual_match,
                'Tithe Match': tithe_match
            })
    
    return discrepancies

def write_audit_report(discrepancies):
    """Write discrepancies to an audit report CSV file."""
    with open(AUDIT_REPORT, mode='w', newline='') as file:
        fieldnames = ['Timestamp', 'Member ID', 'Amount', 'Ritual Match', 'Tithe Match']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(discrepancies)

# Main audit function
def audit_logs():
    transaction_log = load_log(TRANSACTION_LOG)
    ritual_log = load_log(RITUAL_LOG)
    tithe_log = load_log(TITHE_LOG)

    discrepancies = find_discrepancies(transaction_log, ritual_log, tithe_log)
    write_audit_report(discrepancies)

    total_transactions = len(transaction_log) + len(ritual_log) + len(tithe_log)
    unique_transactions = len(transaction_log)  # Assuming unique by transaction ID

    print(f"Audit complete. Discrepancies found: {len(discrepancies)}")
    print(f"Total entries analyzed across logs: {total_transactions}")
    print(f"Unique transactions analyzed: {unique_transactions}")
    print("See audit_report.csv for details.")

# Run audit if script is executed directly
if __name__ == "__main__":
    audit_logs()
