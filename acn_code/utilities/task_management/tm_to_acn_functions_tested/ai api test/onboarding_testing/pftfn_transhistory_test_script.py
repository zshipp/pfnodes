from db_manager import DBConnectionManager
from password_map_loader import PasswordMapLoader
import json
from datetime import datetime

def write_user_history_to_file(db_manager, user_address):
    """Get user's transaction history and write to file for analysis."""
    conn = db_manager.spawn_psycopg2_db_connection('accelerandochurch')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                date,
                from_address,
                to_address,
                -- Use deliver_max_* fields for token transactions
                deliver_max_value AS amount,
                deliver_max_currency AS currency,
                deliver_max_issuer AS issuer,
                (memos->0->'type')::TEXT AS memo_type, -- Extract the first memo's type
                (memos->0->'data')::TEXT AS memo_data, -- Extract the first memo's data
                tx_json
            FROM xrpl_raw_transactions
            WHERE (from_address = %s OR to_address = %s)
                AND (from_address = 'r4yc85M1hwsegVGZ1pawpZPwj65SVs8PzD' 
                    OR to_address = 'r4yc85M1hwsegVGZ1pawpZPwj65SVs8PzD')
            ORDER BY date ASC
        """, (user_address, user_address))
        
        transactions = cursor.fetchall()
        
        # Convert to list of dicts
        fields = ['date', 'from_address', 'to_address', 'amount', 'currency', 'issuer', 'memo_type', 'memo_data', 'tx_json']
        transactions = [dict(zip(fields, tx)) for tx in transactions]
        
    finally:
        cursor.close()
        conn.close()
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_history_{user_address[:8]}_{timestamp}.json"
    
    # Calculate some statistics
    total_transactions = len(transactions)
    total_chars = sum(len(str(tx)) for tx in transactions)
    memo_chars = sum(len(str(tx.get('memo_data', ''))) for tx in transactions)
    
    print(f"\nStatistics for {user_address}:")
    print(f"Total transactions: {total_transactions}")
    print(f"Total characters: {total_chars:,}")
    print(f"Total memo characters: {memo_chars:,}")
    
    # Write full data to file
    with open(filename, 'w') as f:
        json.dump(transactions, f, indent=2, default=str)
    
    print(f"\nFull data written to: {filename}")
    
    # Create a structured summary by task
    tasks = {}
    for tx in transactions:
        # Extract task ID from memo_type if it exists
        task_id = tx['memo_type'].split('__')[-1] if '__' in tx['memo_type'] else tx['memo_type']
        
        if task_id not in tasks:
            tasks[task_id] = []
            
        summary_tx = {
            'date': str(tx['date'].date()),
            'direction': 'sent' if tx['from_address'] == user_address else 'received',
            'memo_type': tx['memo_type'],
            'memo_data': tx['memo_data'][:900] if tx['memo_data'] else None,
            'value': f"{tx['amount']} {tx['currency']}" if tx['amount'] else None  # Removed issuer from the value
        }

       
        tasks[task_id].append(summary_tx)
    
    # Convert to a list, sorting special transactions first
    special_types = ['INITIATION_REWARD', 'INITIATION_RITE', 'discord_wallet_funding']
    summary = []
    
    # Add special transactions first
    for type_name in special_types:
        if type_name in tasks:
            summary.append({
                'task_type': type_name,
                'interactions': tasks.pop(type_name)
            })
    
    # Add regular task sequences
    for task_id, interactions in tasks.items():
        summary.append({
            'task_id': task_id,
            'interactions': interactions
        })
    
    summary_filename = f"user_history_{user_address[:8]}_{timestamp}_summary.json"
    with open(summary_filename, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary data written to: {summary_filename}")

if __name__ == "__main__":
    # Initialize password loader and db manager
    pw_loader = PasswordMapLoader()
    
    # Create password map
    pw_map = {
        'accelerandochurch__postgresconnstring': pw_loader.get_password('ACCELERANDOCHURCH__POSTGRESCONNSTRING')
    }
    
    db_manager = DBConnectionManager(pw_map)
    
    # Test with addresses
    test_addresses = [
        "rLiqoRjzk2ZCjfYpkgDwjvHKTLBu9xCKyk",  # Example address
        # Add more test addresses here
    ]
    
    for address in test_addresses:
        print(f"\nProcessing {address}")
        write_user_history_to_file(db_manager, address)