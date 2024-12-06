import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountTx
import time
from datetime import datetime, timedelta
from psycopg2.extras import Json
from db_manager import DBConnectionManager

def decode_memo(memo_data):
    """Decode hex memo data to text."""
    try:
        return bytes.fromhex(memo_data).decode('utf-8')
    except:
        return "[Unable to decode memo]"

def store_transaction(db_manager, tx_data, tx_hash, ledger_index):
    """Store a transaction in the database."""
    conn = db_manager.spawn_psycopg2_db_connection('accelerandochurch')
    cur = conn.cursor()
    
    try:
        # Extract basic transaction data
        date = datetime.fromtimestamp(tx_data.get('date', 0) + 946684800)  # Ripple epoch
        from_address = tx_data.get('Account')
        to_address = tx_data.get('Destination')
        fee = float(tx_data.get('Fee', 0)) / 1_000_000  # Convert from drops to XRP
        
        # Extract amount and currency
        amount_data = tx_data.get('Amount', {})
        if isinstance(amount_data, dict):
            amount = float(amount_data.get('value', 0))
            currency = amount_data.get('currency', '')
        else:
            amount = float(amount_data) / 1_000_000  # Convert from drops to XRP
            currency = 'XRP'
        
        # Extract memo data
        memos = tx_data.get('Memos', [{}])
        if memos:
            memo = memos[0].get('Memo', {})
            memo_type = decode_memo(memo.get('MemoType', ''))
            memo_format = decode_memo(memo.get('MemoFormat', ''))
            memo_data = decode_memo(memo.get('MemoData', ''))
        else:
            memo_type = memo_format = memo_data = ''
        
        # Insert into database - Updated table name to match db_manager.py
        cur.execute("""
            INSERT INTO xrpl_raw_transactions 
            (tx_hash, ledger_index, date, from_address, to_address, 
             amount, currency, fee, memo_type, memo_format, memo_data, tx_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tx_hash) DO NOTHING
            RETURNING id;
        """, (
            tx_hash, ledger_index, date, from_address, to_address,
            amount, currency, fee, memo_type, memo_format, memo_data,
            Json(tx_data)
        ))
        
        inserted_id = cur.fetchone()
        conn.commit()
        return inserted_id is not None  # Return True if inserted, False if skipped due to conflict

    except Exception as e:
        print(f"Error storing transaction {tx_hash}: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_latest_stored_ledger(db_manager):
    """Get the latest ledger index from stored transactions."""
    conn = db_manager.spawn_psycopg2_db_connection('accelerandochurch')
    cur = conn.cursor()
    try:
        # Updated table name to match db_manager.py
        cur.execute("SELECT MAX(ledger_index) FROM xrpl_raw_transactions")
        result = cur.fetchone()
        return result[0] if result else None
    finally:
        cur.close()
        conn.close()

def scrape_transactions(db_manager, start_ledger=None, end_ledger=None):
    """Scrape all transactions between foundation node and users."""
    try:
        client = JsonRpcClient("https://xrplcluster.com")
        foundation_address = "r4yc85M1hwsegVGZ1pawpZPwj65SVs8PzD"
        
        print(f"Starting transaction scrape...")
        if start_ledger and end_ledger:
            print(f"Ledger range: {start_ledger} to {end_ledger}")
        
        total_processed = 0
        total_stored = 0
        batch_size = 200
        marker = None

        while True:
            print(f"\nFetching batch (processed so far: {total_processed})...")
            
            request_params = {
                'account': foundation_address,
                'limit': batch_size
            }
            
            if start_ledger and end_ledger:
                request_params.update({
                    'ledger_index_min': start_ledger,
                    'ledger_index_max': end_ledger
                })
            
            if marker:
                request_params['marker'] = marker
            
            request = AccountTx(**request_params)
            response = client.request(request)
            
            if not response.is_successful():
                print(f"Error fetching transactions: {response.result}")
                continue
            
            transactions = response.result.get('transactions', [])
            if not transactions:
                print("No more transactions found")
                break
            
            # Process each transaction
            for tx in transactions:
                tx_data = tx.get('tx_json', {})
                tx_hash = tx.get('hash')
                ledger_index = tx.get('ledger_index')
                
                print(f"\nProcessing transaction: {tx_hash}")
                print(f"Ledger: {ledger_index}")
                
                try:
                    if store_transaction(db_manager, tx_data, tx_hash, ledger_index):
                        total_stored += 1
                        print("Transaction stored successfully")
                except Exception as e:
                    print(f"Error storing transaction: {e}")
            
            total_processed += len(transactions)
            
            # Get marker for next batch
            marker = response.result.get('marker')
            if not marker:
                print("No more transactions to fetch")
                break
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        print(f"\nScraping complete!")
        print(f"Total transactions processed: {total_processed}")
        print(f"Total transactions stored: {total_stored}")
            
    except Exception as e:
        print(f"Error during scraping: {e}")

def run_scraper(db_manager):
    """Main function to run the scraper."""
    print("\nChecking latest stored ledger...")
    latest_ledger = get_latest_stored_ledger(db_manager)
    
    if latest_ledger:
        print(f"Found existing transactions up to ledger {latest_ledger}")
        start_ledger = latest_ledger + 1
        # Set end_ledger to None to get all transactions up to current
        scrape_transactions(db_manager, start_ledger=start_ledger, end_ledger=None)
    else:
        print("No existing transactions found, starting fresh scrape")
        # Scrape everything
        scrape_transactions(db_manager)

if __name__ == "__main__":
    from password_map_loader import PasswordMapLoader

    # Initialize the PasswordMapLoader
    password_loader = PasswordMapLoader(env_file_path=".env")

    # Construct the pw_map dynamically
    pw_map = {
        "accelerandochurch__postgresconnstring": password_loader.get_password("ACCELERANDOCHURCH__POSTGRESCONNSTRING")
    }

    # Initialize the DBConnectionManager with the constructed pw_map
    db_manager = DBConnectionManager(pw_map)
    run_scraper(db_manager)