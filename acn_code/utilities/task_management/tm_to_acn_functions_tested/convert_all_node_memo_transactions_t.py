import pandas as pd
import numpy as np
from datetime import datetime

class ACNTaskManagement:
    def __init__(self):
        pass
        
    def convert_all_node_memo_transactions_to_required_collab_generation(self, all_node_memo_transactions):
        """
        Takes all memo transactions and identifies collaboration requests that need processing
        """
        # Get the most recent memo for each memo_type (keeps track of latest status of each request)
        most_recent_memo = all_node_memo_transactions.sort_values('datetime').groupby('memo_type').last()['memo_data']
        
        # Filter transactions to only get collaboration requests
        collab_request_cue = all_node_memo_transactions[all_node_memo_transactions['memo_data'].apply(lambda x: 
                                                                 'REQUEST_ACN_COLLAB' in x)].sort_values('datetime')
        
        # For each request, look up its most recent status from most_recent_memo
        collab_request_cue['most_recent_status'] = collab_request_cue['memo_type'].map(most_recent_memo)
        
        # Mark as requiring work if latest status still shows as a request
        collab_request_cue['requires_work'] = collab_request_cue['most_recent_status'].apply(lambda x: 'REQUEST_ACN_COLLAB' in x)
        
        return collab_request_cue

    def quick_verify_collab_request_processing(self):
        """
        Test the collaboration request processing with mock memo transactions
        """
        # Create mock memo transactions DataFrame
        mock_transactions = pd.DataFrame([
            # Initial collab request
            {
                'datetime': '2024-11-05 10:00:00',
                'memo_type': 'REQUEST_1',
                'memo_data': 'REQUEST_ACN_COLLAB ___ Want to collaborate on docs',
                'memo_format': 'user1'
            },
            # Another request still needing work
            {
                'datetime': '2024-11-05 11:00:00',
                'memo_type': 'REQUEST_2',
                'memo_data': 'REQUEST_ACN_COLLAB ___ UI collaboration needed',
                'memo_format': 'user2'
            },
            # A request that's been processed (accepted)
            {
                'datetime': '2024-11-05 12:00:00',
                'memo_type': 'REQUEST_1',
                'memo_data': 'ACCEPTANCE ___ Will collaborate on docs',
                'memo_format': 'user1'
            }
        ])
        
        # Convert datetime strings to datetime objects
        mock_transactions['datetime'] = pd.to_datetime(mock_transactions['datetime'])

        # Process the mock transactions
        result = self.convert_all_node_memo_transactions_to_required_collab_generation(mock_transactions)
        
        # Save results
        result.to_csv('collab_request_processing_verification.csv')
        
        # Print summary
        print("\nCollaboration Requests Status:")
        print(f"Total requests found: {len(result)}")
        print(f"Requests needing work: {len(result[result['requires_work']])}")
        print("\nDetailed Results:")
        print(result[['memo_type', 'memo_data', 'most_recent_status', 'requires_work']].to_string())

if __name__ == "__main__":
    acn = ACNTaskManagement()
    acn.quick_verify_collab_request_processing()