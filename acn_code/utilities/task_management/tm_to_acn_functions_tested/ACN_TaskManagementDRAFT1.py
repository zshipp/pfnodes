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

    def phase_1_construct_required_post_fiat_generation_cue(self, all_account_info):
        """ This is where the dataframe of requested tasks come from 
        Google Docs are appended to the dataframe as well. Operates
        on most recent tasks only 
        
        account_to_study = self.user_wallet.classic_address
        #account_to_study
        all_account_info =self.generic_pft_utilities.get_memo_detail_df_for_account(account_address=account_to_study,
                    transaction_limit=5000)
        """ 

        simplified_task_frame = self.generic_pft_utilities.convert_all_account_info_into_simplified_task_frame(all_account_info=
                                                                all_account_info)
        most_recent_tasks = simplified_task_frame.sort_values('datetime').copy().groupby('task_id').last()
        required_post_fiat_generation_cue = most_recent_tasks[most_recent_tasks['full_output'].apply(lambda x: 
                                                                'REQUEST_POST_FIAT ___' in x)]
        required_post_fiat_generation_cue['google_doc']=None
        if len(required_post_fiat_generation_cue)>0:
            print('moo')
            required_post_fiat_generation_cue['google_doc']= required_post_fiat_generation_cue.apply(lambda x: self.get_most_recent_google_doc_for_user(user_account=x['user_account'],
                                                                                                    all_account_info=all_account_info),axis=1)
        return required_post_fiat_generation_cu

    def phase_1_construct_required_acn_generation_cue(self, all_account_info):
    """
    Constructs a DataFrame of recent generation tasks specifically for ACN,
    linking Google Docs and filtering by ACN-specific cues.

    Parameters:
    - all_account_info: DataFrame containing transaction details for ACN.

    Returns:
    - DataFrame of required generation tasks for ACN, including the latest linked Google Doc for each user.
    """
    # Step 1: Convert all account info into a simplified task DataFrame for ACN
    simplified_task_frame = self.generic_acn_utilities.convert_all_account_info_into_simplified_task_frame(
        all_account_info=all_account_info
    )

    # Step 2: Filter for the most recent tasks related to ACN generation
    most_recent_tasks = simplified_task_frame.sort_values('datetime').copy().groupby('task_id').last()
    required_acn_generation_cue = most_recent_tasks[
        most_recent_tasks['full_output'].apply(lambda x: 'REQUEST_ACN_GENERATION ___' in x)
    ]

    # Step 3: Initialize Google Doc column and fetch the latest ACN doc for each user if tasks are present
    required_acn_generation_cue['google_doc'] = None
    if len(required_acn_generation_cue) > 0:
        required_acn_generation_cue['google_doc'] = required_acn_generation_cue.apply(
            lambda x: self.get_most_recent_google_doc_for_user(
                user_account=x['user_account'],
                all_account_info=all_account_info
            ),
            axis=1
        )

    return required_acn_generation_cue

    def phase_1_consolidate_acn_pft_generation_cues(self, all_acn_account_info, all_pft_account_info):
    """
    Consolidates generation tasks from both ACN and PFT sources into a single DataFrame.
    
    Parameters:
    - all_acn_account_info: Data for all ACN-specific account transactions.
    - all_pft_account_info: Data for all PFT-specific account transactions.
    
    Returns:
    - DataFrame with combined generation cues from both ACN and PFT systems.
    """
    # Generate the generation DataFrames for ACN and PFT individually
    acn_generation_cue_df = self.phase_1_construct_required_acn_generation_cue(all_acn_account_info)
    pft_generation_cue_df = self.phase_1_construct_required_post_fiat_generation_cue(all_pft_account_info)

    # Add a system label to distinguish between ACN and PFT tasks
    acn_generation_cue_df['system'] = 'ACN'
    pft_generation_cue_df['system'] = 'PFT'

    # Standardize column names if necessary to ensure compatibility for concatenation
    if 'google_doc' not in acn_generation_cue_df.columns:
        acn_generation_cue_df['google_doc'] = None
    if 'google_doc' not in pft_generation_cue_df.columns:
        pft_generation_cue_df['google_doc'] = None

    # Concatenate the DataFrames, maintaining order by timestamp if desired
    consolidated_generation_cue_df = pd.concat([acn_generation_cue_df, pft_generation_cue_df]).reset_index(drop=True)

    return consolidated_generation_cue_df


    

