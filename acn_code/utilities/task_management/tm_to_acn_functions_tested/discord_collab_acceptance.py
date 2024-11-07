import csv

# Mock utilities to simulate generic_acn_utilities
class MockACNUtilities:
    @staticmethod
    def spawn_user_wallet_from_seed(seed):
        # Mocked wallet generation from seed
        return f"wallet_from_seed_{seed}"
    
    @staticmethod
    def get_memo_detail_df_for_account(wallet_address):
        # Mocked method to simulate account transactions
        return [
            {"task_id": "2024-08-17_17:57__TO94", "acceptance": ""},
            {"task_id": "2024-08-18_17:00__XX45", "acceptance": "accepted"}
        ]
    
    @staticmethod
    def convert_all_account_info_into_outstanding_task_df(account_memo_detail_df):
        # Mocked function to simulate outstanding tasks DataFrame
        return {entry["task_id"]: entry for entry in account_memo_detail_df if entry["acceptance"] == ""}

    @staticmethod
    def construct_standardized_xrpl_memo(memo_data, memo_format, memo_type):
        # Mocked memo construction
        return f"{memo_type}::{memo_format}::{memo_data}"

    @staticmethod
    def send_PFT_with_info(sending_wallet, amount, memo, destination_address):
        # Mocked PFT transaction sending
        return {"clean_string": f"Sent {amount} PFT to {destination_address} with memo: {memo}"}

    @staticmethod
    def extract_transaction_info_from_response_object(response_object):
        # Mocked transaction info extraction
        return response_object

# Standalone function for testing
def discord_task_acceptance_test(seed_to_work, user_name, task_id_to_accept, acceptance_string):
    """ 
    Example Params:
    seed_to_work = 's___'
    user_name = '.goodalexander'
    task_id_to_accept = '2024-08-17_17:57__TO94'
    acceptance_string = "I will get this done as soon as I am able" 
    """
    # Create instance of mock utilities
    acn_utilities = MockACNUtilities()
    
    # Spawn wallet and simulate account transactions
    wallet = acn_utilities.spawn_user_wallet_from_seed(seed=seed_to_work)
    wallet_address = wallet
    all_wallet_transactions = acn_utilities.get_memo_detail_df_for_account(wallet_address)
    pf_df = acn_utilities.convert_all_account_info_into_outstanding_task_df(all_wallet_transactions)
    
    # Check if the task ID is valid and outstanding
    valid_task_ids_to_accept = list(pf_df.keys())
    if task_id_to_accept in valid_task_ids_to_accept:
        print('valid task ID proceeding to accept')
        
        # Prepare memo for task acceptance
        formatted_acceptance_string = 'ACCEPTANCE REASON ___ ' + acceptance_string
        acceptance_memo = acn_utilities.construct_standardized_xrpl_memo(
            memo_data=formatted_acceptance_string, 
            memo_format=user_name, 
            memo_type=task_id_to_accept
        )
        
        # Simulate sending transaction
        acceptance_response = acn_utilities.send_PFT_with_info(
            sending_wallet=wallet, 
            amount=1, 
            memo=acceptance_memo, 
            destination_address="acn_node_address"
        )
        
        # Simulate extracting transaction info
        transaction_info = acn_utilities.extract_transaction_info_from_response_object(acceptance_response)
        output_string = transaction_info['clean_string']
    else:
        print('task ID already accepted or not valid')
        output_string = 'task ID already accepted or not valid'
    
    # Log output to CSV
    with open('acn_task_acceptance_test_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write header if file is empty
        if file.tell() == 0:
            writer.writerow(['task_id', 'user_name', 'memo', 'wallet', 'status'])
        # Write transaction log
        writer.writerow([task_id_to_accept, user_name, acceptance_memo, wallet, output_string])
    
    return output_string

# Run the function with test parameters
if __name__ == "__main__":
    # Test parameters
    seed_to_work = 's___'
    user_name = '.goodalexander'
    task_id_to_accept = '2024-08-17_17:57__TO94'
    acceptance_string = "I will get this done as soon as I am able"
    
    # Execute the test and print the result
    response = discord_task_acceptance_test(seed_to_work, user_name, task_id_to_accept, acceptance_string)
    print("Function output:", response)
