import pandas as pd
import numpy as np

# Sample data for all_node_memo_transactions
data = {
    'user_account': ['user1', 'user2', 'user1', 'user3', 'user4', 'user5'],
    'memo_type': ['INITIATION_REWARD', 'INITIATION_RITE', 'INITIATION_REWARD', 'INITIATION_RITE', 'INITIATION_REWARD', 'INITIATION_RITE'],
    'memo_data': ['reward1', 'rite2_longer_than_10', 'reward2', 'rite3', 'reward4', 'rite5_longer_than_10'],
    'memo_format': ['text', None, 'text', None, 'text', None],
    'directional_pft': [1.0, None, 2.0, None, 3.0, None]
}

# Creating a DataFrame
all_node_memo_transactions = pd.DataFrame(data)

# Define the class and function
class ACNClass:
    def output_initiation_rite_df(self, all_node_memo_transactions):
        initiation_rewards = all_node_memo_transactions[all_node_memo_transactions['memo_type'] == 'INITIATION_REWARD'][
            ['user_account', 'memo_data', 'memo_format', 'directional_pft']
        ].groupby('user_account').last()[['memo_data', 'directional_pft', 'memo_format']]
        
        rites = all_node_memo_transactions[all_node_memo_transactions['memo_type'] == "INITIATION_RITE"][
            ['user_account', 'memo_data']
        ].groupby('user_account').last()
        rites.columns = ['initiation_rite']

        initiation_rite_cue_df = pd.concat([rites, initiation_rewards], axis=1).reset_index()
        
        initiation_rite_cue_df['requires_work'] = np.where(
            (initiation_rite_cue_df['initiation_rite'].apply(lambda x: len(str(x)) > 10)) &
            (initiation_rite_cue_df['memo_data'].apply(lambda x: 'INITIATION_REWARD' not in str(x))),
            1, 0
        )
        return initiation_rite_cue_df

# Instantiate and run the test function
acn = ACNClass()
result_df = acn.output_initiation_rite_df(all_node_memo_transactions)

# Save the result to a CSV file for inspection
result_df.to_csv("initiation_rite_data.csv", index=False)

print("The result has been saved to 'initiation_rite_data.csv'")
