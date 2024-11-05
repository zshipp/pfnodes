"""
ACN Task Management
This file handles the task management system for the Accelerando Church Node (ACN).
It includes functions for proposing tasks, tracking task status, verifying completion, and logging.
"""

import datetime
import re
import psycopg2
import logging
import pandas as pd
import numpy as np

# ACN-specific imports, mirroring the structure from PFT
from GenericACNUtilities import *
from password_map_loader import PasswordMapLoader
from ACN_Utilities import ACNUtilities

class ACNTaskManagement:
    def __init__(self, pw_map):
       self.pw_map = pw_map
       # Set up default model and initialize OpenAI request tool
       self.default_task_model = 'chatgpt-4o-latest'
       self.openai_request_tool = OpenAIRequestTool(pw_map=self.pw_map)
        
       # Initialize utilities with node information
       self.generic_acn_utilities = GenericACNUtilities(pw_map=self.pw_map, node_name=NODE_NAME)
       self.node_address = NODE_ADDRESS
       self.node_seed = self.pw_map.get("acn__v1xrpsecret")
       self.node_wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(seed=self.node_seed)
        
       # Set up database connection manager and status
       self.stop_threads = False
       self.db_connection_manager = DBConnectionManager(pw_map=pw_map)
       # self.open_ai_request_tool = OpenAIRequestTool(pw_map=self.pw_map)

   def output_initiation_rite_df(self, all_node_memo_transactions):
    """
    Processes all initiation rites and rewards for the ACN.
    
    all_node_transactions = self.generic_acn_utilities.get_all_cached_transactions_related_to_account(self.node_address).copy()
    all_node_memo_transactions = self.generic_acn_utilities.get_memo_detail_df_for_account(account_address=self.node_address, pft_only=False).copy()
    """
    # Extract initiation rewards, grouping by user account for the latest status
    initiation_rewards = all_node_memo_transactions[all_node_memo_transactions['memo_type'] == 'INITIATION_REWARD'][
        ['user_account', 'memo_data', 'memo_format', 'directional_pft']
    ].groupby('user_account').last()[['memo_data', 'directional_pft', 'memo_format']]
    
    # Extract initiation rites for ACN, grouped by user account
    rites = all_node_memo_transactions[all_node_memo_transactions['memo_type'] == "INITIATION_RITE"][
        ['user_account', 'memo_data']
    ].groupby('user_account').last()
    rites.columns = ['initiation_rite']

    # Merge the initiation rites and rewards to create a consolidated DataFrame
    initiation_rite_cue_df = pd.concat([rites, initiation_rewards], axis=1).reset_index()
    
    # Add a column to flag rites that need further processing (based on memo content)
    initiation_rite_cue_df['requires_work'] = np.where(
        (initiation_rite_cue_df['initiation_rite'].apply(lambda x: len(str(x)) > 10)) &
        (initiation_rite_cue_df['memo_data'].apply(lambda x: 'INITIATION_REWARD' not in str(x))),
        1, 0
    )
    return initiation_rite_cue_df

    

