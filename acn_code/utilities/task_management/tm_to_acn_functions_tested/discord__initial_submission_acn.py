import pandas as pd
import csv
from datetime import datetime

# Mock class to simulate `generic_acn_utilities` behavior
class MockACNUtilities:
    def spawn_user_wallet_from_seed(self, seed):
        # Mock wallet object with a simple structure
        class MockWallet:
            def __init__(self):
                self.classic_address = "rMockWalletAddress"
        return MockWallet()
    
    def get_memo_detail_df_for_account(self, wallet_address):
        # Returns a mock DataFrame as if fetching past transactions
        return pd.DataFrame({
            'acceptance': ['accepted', ''],  # Simulating one accepted and one unaccepted task
            'task_id': ['2024-07-01_15:11__CR11', '2024-07-01_15:12__CR12']
        }).set_index('task_id')
    
    def convert_all_account_info_into_outstanding_task_df(self, account_memo_detail_df):
        # Just return the DataFrame as-is, assuming it's preprocessed for outstanding tasks
        return account_memo_detail_df
    
    def construct_standardized_xrpl_memo(self, memo_data, memo_format, memo_type):
        # Mock memo construction by concatenating inputs
        return f"{memo_type}::{memo_format}::{memo_data}"
    
    def send_PFT_with_info(self, sending_wallet, amount, memo, destination_address, url=None):
        # Mock transaction response with a success message
        return {"status": "success", "clean_string": "Transaction successful"}
    
    def extract_transaction_info_from_response_object(self, completion_response):
        # Return the "clean_string" from the mock response
        return completion_response

class TaskManagementACN:
    def __init__(self, generic_acn_utilities, node_address):
        self.generic_acn_utilities = generic_acn_utilities
        self.node_address = node_address

    def discord__initial_collab_submission(self, seed_to_work, user_name, collab_id_to_submit, initial_completion_string):
        """
        Submits an initial completion for a collaboration if the collaboration ID is valid and accepted.
        """
        wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(seed=seed_to_work)
        wallet_address = wallet.classic_address
        all_wallet_transactions = self.generic_acn_utilities.get_memo_detail_df_for_account(wallet_address).copy()
        pf_df = self.generic_acn_utilities.convert_all_account_info_into_outstanding_task_df(account_memo_detail_df=all_wallet_transactions)

        valid_collab_ids_to_submit_for_completion = list(pf_df[pf_df['acceptance'] != ''].index)
        if collab_id_to_submit in valid_collab_ids_to_submit_for_completion:
            print('Valid collaboration ID proceeding to submit for completion')
            formatted_completed_justification_string = 'COLLAB COMPLETION JUSTIFICATION ___ ' + initial_completion_string
            completion_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=formatted_completed_justification_string, 
                memo_format=user_name, 
                memo_type=collab_id_to_submit
            )
            completion_response = self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=wallet, 
                amount=1, 
                memo=completion_memo, 
                destination_address=self.node_address
            )
            transaction_info = self.generic_acn_utilities.extract_transaction_info_from_response_object(completion_response)
            output_string = transaction_info['clean_string']
        else:
            print('Collab ID has not been accepted or is not present')
            output_string = 'Collab ID has not been accepted or is not present'
        
        # Log result to CSV
        self.log_to_csv(user_name, collab_id_to_submit, output_string)
        return output_string

    def log_to_csv(self, user_name, collab_id, result):
        """
        Logs the submission attempt to a CSV file with timestamp, user, collab ID, and result.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "Timestamp": timestamp,
            "User": user_name,
            "Collab ID": collab_id,
            "Result": result
        }
        
        # Append to CSV
        with open("collab_submission_log.csv", mode="a", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=log_entry.keys())
            if file.tell() == 0:  # Check if file is empty to write headers
                writer.writeheader()
            writer.writerow(log_entry)

# Testing the function with mock utilities
if __name__ == "__main__":
    # Initialize TaskManagementACN with mock utilities and test
    task_manager = TaskManagementACN(MockACNUtilities(), node_address="rNodeAddress")

    # Test submission
    test_output = task_manager.discord__initial_collab_submission(
        seed_to_work="s____S",
        user_name=".goodalexander",
        collab_id_to_submit="2024-07-01_15:11__CR11",
        initial_completion_string="Initial completion of the collab"
    )
    print("Test Output:", test_output)
