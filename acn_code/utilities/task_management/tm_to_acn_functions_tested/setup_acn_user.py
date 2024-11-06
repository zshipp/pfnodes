import pandas as pd
import numpy as np

class ACNTaskManagement:
    class MockWallet:
        def __init__(self, address):
            self.classic_address = address
            
    class MockUtilities:
        def spawn_user_wallet_from_seed(self, seed):
            return ACNTaskManagement.MockWallet("rTestAddress123")
            
        def get_memo_detail_df_for_account(self, account_address, pft_only):
            return pd.DataFrame({
                'memo_type': ['google_doc_context_link'],
                'memo_data': ['existing_doc_link'],
                'memo_format': ['test_user'],
                'user_account': ['rTestAddress123']
            })
            
        def check_if_there_is_funded_account_at_front_of_google_doc(self, google_url):
            return 15  # Mock balance
            
        def construct_standardized_xrpl_memo(self, memo_data, memo_format, memo_type):
            return f"MEMO: {memo_data}"
            
        def send_PFT_with_info(self, sending_wallet, amount, destination_address, memo):
            return {"status": "success"}
            
        def extract_transaction_info_from_response_object(self, response):
            return {"clean_string": "Transaction successful"}

    def __init__(self):
        self.node_seed = "test_seed"
        self.node_address = "rNodeAddress123"
        self.generic_acn_utilities = self.MockUtilities()
        self.generic_pft_utilities = self.MockUtilities()
        
    def process_user_setup(self, account_seed, google_doc_link, username):
        """The actual setup logic"""
        error_string = '' 
        wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(seed=account_seed)
        account_address = wallet.classic_address

        # Check existing google docs
        all_account_transactions = self.generic_acn_utilities.get_memo_detail_df_for_account(
            account_address=self.node_address, 
            pft_only=False
        )
        all_google_docs = all_account_transactions[
            all_account_transactions['memo_type'].apply(lambda x: 'google_doc_context_link' in x) 
            & (all_account_transactions['user_account'] == account_address)
        ][['memo_type','memo_data','memo_format','user_account']]
        
        google_doc = ''
        if len(all_google_docs)>0:
            google_doc_row = all_google_docs.tail(1)
            google_doc = list(google_doc_row['memo_data'])[0]
            print(f'Already has a google doc: {google_doc}')
        
        if google_doc == '':
            print('sending google doc')
            balance = self.generic_acn_utilities.check_if_there_is_funded_account_at_front_of_google_doc(
                google_url=google_doc_link
            )
            print(f'XRPL balance is {balance}')
            
            if balance <= 12:
                error_string = error_string+'Insufficient XRP Balance'
            if balance > 12:
                google_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                    memo_data=google_doc_link, 
                    memo_format=username, 
                    memo_type='google_doc_context_link'
                )
                response = self.generic_pft_utilities.send_PFT_with_info(
                    sending_wallet=wallet, 
                    amount=1, 
                    destination_address=self.node_address, 
                    memo=google_memo
                )
                error_string = self.generic_acn_utilities.extract_transaction_info_from_response_object(
                    response
                )['clean_string']
        
        return {
            'account_seed': account_seed,
            'google_doc': google_doc if google_doc else google_doc_link,
            'username': username,
            'status': error_string if error_string else 'Success',
            'balance': balance if 'balance' in locals() else 'N/A',
            'has_existing_doc': bool(google_doc)
        }

if __name__ == "__main__":
    # Test cases
    test_cases = [
        {
            "account_seed": "sTest123",
            "google_doc_link": "https://docs.google.com/test1",
            "username": "test_user1"
        },
        {
            "account_seed": "sTest456",
            "google_doc_link": "https://docs.google.com/test2",
            "username": "test_user2"
        }
    ]
    
    results = []
    acn = ACNTaskManagement()
    for test in test_cases:
        print("\n=== Testing with new user ===")
        result = acn.process_user_setup(
            account_seed=test["account_seed"],
            google_doc_link=test["google_doc_link"],
            username=test["username"]
        )
        results.append(result)
        print(f"Result: {result}")
    
    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv('setup_acn_user_verification.csv', index=False)
    print("\nResults saved to setup_acn_user_verification.csv")