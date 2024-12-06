import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountTx
import time
from datetime import datetime, timedelta
import json

FOUNDATION_ADDRESS = "r4yc85M1hwsegVGZ1pawpZPwj65SVs8PzD"
XRPL_ENDPOINT = "https://xrplcluster.com"
BATCH_SIZE = 50  # Just get 50 transactions for testing

def convert_ripple_time(ripple_time):
    ripple_epoch = datetime(2000, 1, 1)
    timestamp = ripple_epoch + timedelta(seconds=ripple_time)
    return timestamp

def decode_memo(memo_data):
    if not memo_data:
        return None
    try:
        return bytes.fromhex(memo_data).decode('utf-8', errors='replace')
    except:
        return None

def scrape_test_transactions():
    client = JsonRpcClient(XRPL_ENDPOINT)
    marker = None
    all_txs = []
    fetched = 0

    while True:
        try:
            req = AccountTx(
                account=FOUNDATION_ADDRESS,
                limit=BATCH_SIZE,
                marker=marker
            )
            response = client.request(req)
            result = response.result

            txs = result.get('transactions', [])
            if not txs:
                break

            for t in txs:
                tx_data = t
                tx_hash = tx_data.get('hash')
                tx_json = tx_data.get('tx', {})
                ripple_date = tx_json.get('date')
                tx_date = convert_ripple_time(ripple_date) if ripple_date else None

                # Extract memos
                memos_data = []
                memos = tx_json.get('Memos', [])
                for m in memos:
                    memo_obj = m.get('Memo', {})
                    memo_data_hex = memo_obj.get('MemoData')
                    memo_type_hex = memo_obj.get('MemoType')
                    memo_format_hex = memo_obj.get('MemoFormat')
                    memos_data.append({
                        "MemoData": decode_memo(memo_data_hex) if memo_data_hex else None,
                        "MemoType": decode_memo(memo_type_hex) if memo_type_hex else None,
                        "MemoFormat": decode_memo(memo_format_hex) if memo_format_hex else None
                    })

                # Add everything to our collected list
                all_txs.append({
                    "tx_hash": tx_hash,
                    "ledger_index": tx_data.get('ledger_index'),
                    "validated": tx_data.get('validated', False),
                    "transaction_type": tx_json.get('TransactionType'),
                    "account": tx_json.get('Account'),
                    "destination": tx_json.get('Destination'),
                    "amount": tx_json.get('Amount'),
                    "fee": tx_json.get('Fee'),
                    "date": tx_date.isoformat() if tx_date else None,
                    "memos": memos_data,
                    "full_tx": tx_data
                })

                fetched += 1
                if fetched >= 50:
                    break

            if fetched >= 50:
                break

            marker = result.get('marker')
            if not marker:
                break

            time.sleep(0.1)

        except Exception as e:
            print(f"Error: {e}")
            break

    # Output to file
    with open("test_transactions_output.json", "w", encoding="utf-8") as f:
        json.dump(all_txs, f, ensure_ascii=False, indent=4)

    print("Scraping test complete. Results saved to test_transactions_output.json")

if __name__ == "__main__":
    scrape_test_transactions()
