import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountTx
import re
import csv
import time
from datetime import datetime, timedelta

def convert_ripple_time(ripple_time):
    """Convert Ripple timestamp to human readable date."""
    ripple_epoch = datetime(2000, 1, 1)  # Ripple epoch starts from Jan 1, 2000
    timestamp = ripple_epoch + timedelta(seconds=ripple_time)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def get_approximate_date(current_ledger, end_ledger):
    """Calculate approximate date from ledger number."""
    ledger_diff = end_ledger - current_ledger
    minutes_ago = ledger_diff * 2  # Each ledger is ~2 minutes
    current_time = datetime.now()
    approximate_date = current_time - timedelta(minutes=minutes_ago)
    return approximate_date.strftime("%Y-%m-%d")

def decode_memo(memo_data):
    """Decode hex memo data to text."""
    try:
        return bytes.fromhex(memo_data).decode('utf-8')
    except:
        return "[Unable to decode memo]"

def extract_google_doc_link(text):
    """Extract Google Doc links from text."""
    patterns = [
        r'https://docs\.google\.com/\S+',
        r'https://drive\.google\.com/\S+'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def scrape_submissions():
    """Scrape submissions working backwards from most recent."""
    try:
        client = JsonRpcClient("https://xrplcluster.com")
        r4yc_address = "r4yc85M1hwsegVGZ1pawpZPwj65SVs8PzD"
        
        # Start from current ledger
        end_ledger = 92577398  # We can start from this known good ledger
        window_size = 2000  # Smaller window to reduce errors
        
        # Setup CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"pf_submissions_{timestamp}.csv"
        
        csv_headers = [
            'submission_date',
            'submission_tx_hash',
            'submitter_address',
            'google_doc_link',
            'submission_memo',
            'reward_date',
            'reward_tx_hash',
            'reward_memo',
            'ledger_index'
        ]
        
        print(f"Starting from most recent ledger {end_ledger}")
        print(f"Output will be saved to: {csv_filename}")
        print("Press Ctrl+C to stop the scraping at any time")
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
            writer.writeheader()
            
            current_end = end_ledger
            total_processed = 0
            matched_count = 0
            
            try:
                while True:  # Keep going until stopped
                    current_start = max(current_end - window_size, 0)  # Don't go below 0
                    
                    print(f"\nFetching ledgers {current_start} to {current_end}")
                    print(f"Transactions processed so far: {total_processed}")
                    
                    request = AccountTx(
                        account=r4yc_address,
                        limit=200,
                        ledger_index_min=current_start,
                        ledger_index_max=current_end
                    )
                    
                    response = client.request(request)
                    
                    if not response.is_successful():
                        print(f"Error fetching transactions: {response.result}")
                        current_end = current_start  # Move window back
                        continue
                    
                    transactions = response.result.get('transactions', [])
                    if transactions:
                        # First collect rewards in this batch
                        rewards = {}
                        for tx in transactions:
                            tx_data = tx.get('tx_json', {})
                            memo_data = tx_data.get('Memos', [{}])[0].get('Memo', {}).get('MemoData', '')
                            memo_text = decode_memo(memo_data)
                            tx_date = convert_ripple_time(tx_data.get('date', 0))
                            
                            if tx_data.get('Account') == r4yc_address and 'INITIATION_REWARD' in memo_text:
                                recipient = tx_data.get('Destination')
                                if recipient:
                                    rewards[recipient] = {
                                        'date': tx_date,
                                        'memo': memo_text,
                                        'hash': tx.get('hash'),
                                        'ledger_index': tx.get('ledger_index')
                                    }
                        
                        # Then process submissions
                        for tx in transactions:
                            tx_data = tx.get('tx_json', {})
                            if tx_data.get('Account') != r4yc_address:
                                memo_data = tx_data.get('Memos', [{}])[0].get('Memo', {}).get('MemoData', '')
                                memo_text = decode_memo(memo_data)
                                sender = tx_data.get('Account')
                                tx_date = convert_ripple_time(tx_data.get('date', 0))
                                
                                if sender in rewards:
                                    doc_link = extract_google_doc_link(memo_text)
                                    if doc_link:
                                        writer.writerow({
                                            'submission_date': tx_date,
                                            'submission_tx_hash': tx.get('hash'),
                                            'submitter_address': sender,
                                            'google_doc_link': doc_link,
                                            'submission_memo': memo_text[:1000],
                                            'reward_date': rewards[sender]['date'],
                                            'reward_tx_hash': rewards[sender]['hash'],
                                            'reward_memo': rewards[sender]['memo'][:1000],
                                            'ledger_index': tx.get('ledger_index')
                                        })
                                        matched_count += 1
                                        print(f"\nFound match #{matched_count}")
                                        print(f"Date: {tx_date}")
                                        print(f"Link: {doc_link}")
                                        print(f"Ledger: {tx.get('ledger_index')}")
                        
                        total_processed += len(transactions)
                    
                    current_end = current_start  # Move window back
                    time.sleep(0.1)  # Small delay between requests
                    
            except KeyboardInterrupt:
                print("\nScraping stopped by user")
            
            print(f"\nScraping complete!")
            print(f"Total transactions processed: {total_processed}")
            print(f"Total matches found: {matched_count}")
            print(f"Results saved to: {csv_filename}")
                
    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == "__main__":
    scrape_submissions()