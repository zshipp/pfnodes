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
   
def create_multiple_copies_of_df(self, df, n_copies):
        """
        Create multiple copies of a dataframe and add a unique index column.
        Args:
        df (pd.DataFrame): Input dataframe
        n_copies (int): Number of copies to create
        Returns:
        pd.DataFrame: Concatenated dataframe with unique index column
        """
        copies = [df.copy() for _ in range(n_copies)]
        result = pd.concat(copies, ignore_index=True)
        result['unique_index'] = range(len(result))
        return result

def parse_collab_request(self, user_request):
    """
    Parses a collaboration request to extract target user and request details.
    Returns target user identifier and cleaned request.
    """
    # You'd implement logic here to extract user identifier
    # This is just an example pattern
    return target_user_id, cleaned_request

def get_user_context(self, user_id):
    """
    Looks up user's address from database and gets their full context
    """
    # Look up in database
    user_address = self.db_connection_manager.get_user_address(user_id)
    # Get context using existing utilities
    return self.generic_acn_utilities.get_full_user_context_string(account_address=user_address)

def handle_collab_request(self, requesting_full_user_context, user_request):
    """
    Main handler for collaboration requests
    """
    # Parse the request
    target_user_id, cleaned_request = self.parse_collab_request(user_request)
    
    # Get target user's context
    full_target_user_context = self.get_user_context(target_user_id)
    
    # Generate collaboration suggestions
    return self.phase_1_a__n_collab_generator(
        requesting_full_user_context=requesting_full_user_context,  # Fixed
        full_target_user_context=full_target_user_context,
        user_request=cleaned_request
    )

def phase_1_a__initial_collab_generation_api_args(self, requesting_full_user_context, full_target_user_context,
                                                 user_request='I want to help Visc with something related to the Accelerando Church'):
    """ 
    Creates API arguments for collaboration generation, considering both users' contexts.
    
    Parameters:
    requesting_full_user_context: Context of the requesting user
    full_target_user_context: Context of the user they want to collaborate with
    user_request: The specific collaboration request (defaults to ACN-related)
    
    Example:
    account_address = 'r3UHe45BzAVB3ENd21X9LeQngr4ofRJo5n'
    requesting_full_user_context = self.generic_acn_utilities.get_full_user_context_string(account_address=account_address)
    full_target_user_context = self.generic_acn_utilities.get_full_user_context_string(account_address=target_address)
    """ 
    context_augment = f'''<THE USER SPECIFIC COLLABORATION REQUEST STARTS HERE>
    {user_request}
    <THE USER SPECIFIC COLLABORATION REQUEST ENDS HERE>
    
    <TARGET USER CONTEXT STARTS HERE>
    {full_target_user_context}
    <TARGET USER CONTEXT ENDS HERE>'''
    
    full_augmented_context = requesting_full_user_context + context_augment
    
    api_args = {
        "model": self.default_model,
        "messages": [
            {"role": "system", "content": collaboration_generation.phase_1_a__system},
            {"role": "user", "content": collaboration_generation.phase_1_a__user.replace('___FULL_USER_CONTEXT_REPLACE___', full_augmented_context)}
        ]}
    return api_args

def phase_1_a__n_collab_generator(self, requesting_full_user_context, full_target_user_context, 
                                 user_request, n_copies):
    """
    Generates multiple collab suggestions considering both users' contexts.
    
    Parameters:
    requesting_full_user_context (str): Context/history of user requesting the collab
    full_target_user_context (str): Context/history of user they want to collab with
    user_request (str): Specific collab request
    n_copies (int): Number of collab variations to generate
    """
    # Combine contexts and request for API
    user_api_arg = self.phase_1_a__initial_collab_generation_api_args(
        requesting_full_user_context=requesting_full_user_context,
        full_target_user_context=full_target_user_context,
        user_request=user_request
    )
    
    # Create copies for multiple collab generation
    copy_frame = pd.DataFrame([[user_api_arg]])
    copy_frame.columns = ['api_args']
    full_copy_df = self.create_multiple_copies_of_df(df=copy_frame, n_copies=n_copies)
    
    # Generate collabs through async API calls
    async_dict_to_work = full_copy_df.set_index('unique_index')['api_args'].to_dict()
    output = self.openai_request_tool.create_writable_df_for_async_chat_completion(arg_async_map=async_dict_to_work)
    
    result_map = output[['internal_name','choices__message__content']].groupby('internal_name').first()['choices__message__content']
    full_copy_df['output'] = full_copy_df['unique_index'].map(result_map)
    
    # Extract collab details
    full_copy_df['collab_string'] = full_copy_df['output'].apply(
        lambda x: x.split('Final Output |')[-1:][0].split('|')[0].strip()
    )
    full_copy_df['value'] = full_copy_df['output'].apply(
        lambda x: x.split('| Value of Collab |')[-1:][0].replace('|','').strip()
    )
    
    full_copy_df['classification'] = 'COLLAB ' + (full_copy_df['unique_index']+1).astype(str)
    full_copy_df['simplified_string'] = full_copy_df['collab_string'] + ' .. ' + full_copy_df['value']
    
    output_string = '\n'.join(list(full_copy_df['simplified_string']))
    
    return {
        'full_api_output': full_copy_df, 
        'n_collab_output': output_string
    }

    def convert_all_node_memo_transactions_to_required_collab_generation(self, all_node_memo_transactions):
    """
    Takes all memo transactions and identifies collaboration requests that need processing
    
    Input:
    all_node_memo_transactions = self.generic_acn_utilities.get_memo_detail_df_for_account(account_address=self.node_address, pft_only=False).copy()
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

    def setup_acn_user(self, account_seed, google_doc_link, username):
    """ 
        PFN name of this function was "discover_server__initiation_rite"
        EXAMPLE:
        account_seed = 'sEdSqchDCHj29NoRhcsZ8EQfbAkbBJ2'
        google_doc_link='https://docs.google.com/document/d/1M7EW9ocKDnbnSZ1Xa5FanfhRbteVJYV-iNOsvj5bGf4/edit'
        username = 'acn_user'
    """ 
    error_string = '' 
    wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(seed=account_seed)
    account_address = wallet.classic_address

    # Check existing google docs
    all_account_transactions = self.generic_acn_utilities.get_memo_detail_df_for_account(account_address=self.node_address, pft_only=False)
    all_google_docs = all_account_transactions[all_account_transactions['memo_type'].apply(lambda x: 'google_doc_context_link' in x) 
    & (all_account_transactions['user_account'] == account_address)][['memo_type','memo_data','memo_format','user_account']]
    
    google_doc = ''
    if len(all_google_docs)>0:
        google_doc_row = all_google_docs.tail(1)
        google_doc = list(google_doc_row['memo_data'])[0]
        print(f'Already has a google doc: {google_doc}')
    
    if google_doc == '':
        print('sending google doc')
        balance = self.generic_acn_utilities.check_if_there_is_funded_account_at_front_of_google_doc(google_url=google_doc_link)
        print(f'XRPL balance is {balance}')
        if balance <=12:
            error_string = error_string+'Insufficient XRP Balance'
        if balance>12:
            google_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=google_doc_link, 
                memo_format=username, 
                memo_type='google_doc_context_link'
            )
            self.generic_pft_utilities.send_PFT_with_info(
                sending_wallet=wallet, 
                amount=1, 
                destination_address=self.node_address, 
                memo=google_memo
            )
            error_string = self.generic_acn_utilities.extract_transaction_info_from_response_object(xo)['clean_string']
    
    return error_string