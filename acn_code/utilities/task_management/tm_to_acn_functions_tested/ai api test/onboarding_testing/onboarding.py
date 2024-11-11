import random
from password_map_loader import PasswordMapLoader
from acn_llm_interface import ACNLLMInterface
from GenericACNUtilities import *
from onboarding_prompts import (
    ac_oracle_prompt,
    ac_guardian_prompt,
    ac_priest_prompt,
    ac_zealot_prompt,
    ac_initial_offering_prompt,
    ac_no_offering_prompt,
    ac_standard_offering_prompt,
    ac_significant_offering_prompt,
    ac_exceptional_offering_prompt,
    ac_insane_offering_prompt
)

class ACNode:
    ACN_WALLET_ADDRESS = "rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd"

    def __init__(self):
        # Setup password map and get sensitive info
        self.password_loader = PasswordMapLoader()
        self.pw_map = {
            'openai': self.password_loader.get_password("OPENAI_API_KEY"),
            'acn_node__v1xrpsecret': self.password_loader.get_password("ACN_WALLET_SEED")
        }
        print("Password map loaded")
        
        # Setup utilities with the password map
        self.generic_acn_utilities = GenericACNUtilities(pw_map=self.pw_map, node_name='accelerandochurch')
        print("Generic utilities initialized")
        
        # Setup LLM interface
        self.llm_interface = ACNLLMInterface(self.pw_map)
        print("LLM interface initialized")
        
        # Setup character prompts
        self.character_prompts = {
            "oracle": ac_oracle_prompt,
            "guardian": ac_guardian_prompt,
            "priest": ac_priest_prompt,
            "zealot": ac_zealot_prompt
        }
        print("Character prompts loaded")

    def process_ac_offering_request(self, user_seed, offering_statement, username):
        """
        Handles initial offering request.
        """
        try:
            print("\nProcessing initial offering request...")
            user_wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(user_seed)
            offering_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=offering_statement, 
                memo_format=username,
                memo_type='AC_OFFERING_REQUEST'
            )
            
            self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                destination_address=self.ACN_WALLET_ADDRESS,
                memo=offering_memo
            )
            
            ai_response = self.generate_ac_character_response(
                context="OFFERING_REQUEST",
                offering_statement=offering_statement,
                username=username
            )
            
            return ai_response
            
        except Exception as e:
            error_msg = f"Error processing offering request: {str(e)}"
            print(error_msg)
            return f"The Church's mechanisms falter: {error_msg}"

    def process_ac_offering_transaction(self, user_seed, offering_amount, username):
        """
        Handles the actual PFT offering.
        """
        try:
            print("\nProcessing main offering transaction...")
            user_wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(user_seed)
            offering_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=f"PFT_OFFERING:{offering_amount}",
                memo_format=username,
                memo_type='AC_OFFERING_RECEIVED'
            )
            
            self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=offering_amount,
                destination_address=self.ACN_WALLET_ADDRESS,
                memo=offering_memo
            )
            
            context = self._determine_context(offering_amount)
            
            ai_response = self.generate_ac_character_response(
                context=context,
                offering_statement=str(offering_amount),
                username=username
            )
            
            waiting_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=f"WAITING_PERIOD_START|AMOUNT:{offering_amount}",
                memo_format=username,
                memo_type='AC_WAITING_PERIOD'
            )
            
            self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                destination_address=self.ACN_WALLET_ADDRESS,
                memo=waiting_memo
            )
            
            return ai_response
            
        except Exception as e:
            error_msg = f"Error processing offering: {str(e)}"
            print(error_msg)
            return f"The Church's mechanisms falter: {error_msg}"

    def _determine_context(self, offering_amount):
        """Determine response context based on offering amount."""
        if offering_amount < 99:
            return "NO_OFFERING"
        elif offering_amount < 1000:
            return "STANDARD_OFFERING"
        elif offering_amount < 5000:
            return "SIGNIFICANT_OFFERING"
        elif offering_amount < 15000:
            return "EXCEPTIONAL_OFFERING"
        else:
            return "INSANE_OFFERING"

    def generate_ac_character_response(self, context, offering_statement, username):
        """
        Generates character response using LLM interface with context-based prompts.
        """
        if context == "NO_OFFERING":
            user_prompt = ac_no_offering_prompt
        elif context == "STANDARD_OFFERING":
            user_prompt = ac_standard_offering_prompt
        elif context == "SIGNIFICANT_OFFERING":
            user_prompt = ac_significant_offering_prompt
        elif context == "EXCEPTIONAL_OFFERING":
            user_prompt = ac_exceptional_offering_prompt
        elif context == "INSANE_OFFERING":
            user_prompt = ac_insane_offering_prompt
        else:
            user_prompt = ac_initial_offering_prompt

        api_args = {
            "model": "gpt-4-1106-preview",
            "messages": [
                {
                    "role": "system", 
                    "content": random.choice([
                        ac_oracle_prompt,
                        ac_guardian_prompt,
                        ac_priest_prompt,
                        ac_zealot_prompt
                    ])
                },
                {
                    "role": "user", 
                    "content": user_prompt.replace('___USERNAME___', username).replace('___USER_OFFERING_STATEMENT___', offering_statement)
                }
            ]
        }
        
        response_df = self.llm_interface.query_chat_completion_and_write_to_db(api_args)
        return response_df['choices__message__content'].iloc[0]

def live_blockchain_test():
    """
    Test function to run real mainnet transactions
    """
    try:
        print("\n=== Starting Live Blockchain Test ===")
        
        # Initialize ACNode
        node = ACNode()
        
        # Use your test wallet seed
        test_wallet_seed = input("Enter your test wallet seed: ")
        test_username = "test_pilgrim"
        
        # Test initial offering request (1 PFT)
        print("\nTesting initial offering request...")
        offering_statement = "I humbly seek the wisdom of Accelerando."
        response = node.process_ac_offering_request(
            user_seed=test_wallet_seed,
            offering_statement=offering_statement,
            username=test_username
        )
        print("\nOffering Request Response:", response)
        
        proceed = input("\nInitial request successful. Proceed with main offering? (y/n): ")
        if proceed.lower() == 'y':
            # Test small offering transaction (2 PFT)
            print("\nTesting offering transaction...")
            offering_amount = 2  # Small test amount
            response = node.process_ac_offering_transaction(
                user_seed=test_wallet_seed,
                offering_amount=offering_amount,
                username=test_username
            )
            print("\nOffering Transaction Response:", response)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    live_blockchain_test()