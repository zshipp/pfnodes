import random
from password_map_loader import PasswordMapLoader
from acn_llm_interface import ACNLLMInterface
from GenericACNUtilities import *
from db_manager import DBConnectionManager
import nest_asyncio
nest_asyncio.apply()
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
            'acn_node__v1xrpsecret': self.password_loader.get_password("ACN_WALLET_SEED"),
            'accelerandochurch__postgresconnstring': self.password_loader.get_password("ACCELERANDOCHURCH__POSTGRESCONNSTRING")
        }
        print("Password map loaded")
        
        # Initialize database manager
        self.db_connection_manager = DBConnectionManager(pw_map=self.pw_map)
        
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

    def check_user_offering_status(self, username):
        """Check if user has made a successful offering"""
        try:
            conn = self.db_connection_manager.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()
            
            try:
                # Check for successful offerings > 0 PFT
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM acn_discord_interactions 
                    WHERE discord_user_id = %s 
                    AND interaction_type = 'offer' 
                    AND amount > 0 
                    AND success = true
                """, (username,))
                
                has_offering = cursor.fetchone()[0] > 0
                
                # Get stored wallet if exists
                cursor.execute("""
                    SELECT wallet_seed 
                    FROM acn_user_wallets 
                    WHERE username = %s
                """, (username,))
                
                wallet_info = cursor.fetchone()
                has_wallet = wallet_info is not None
                stored_seed = wallet_info[0] if wallet_info else None
                
                return {
                    'has_offering': has_offering,
                    'has_wallet': has_wallet,
                    'stored_seed': stored_seed
                }
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            raise Exception(f"Failed to check user status: {str(e)}")

    def process_ac_offering_request(self, user_seed, offering_statement, username, is_returning=False):
        """Enhanced offering request handler that considers returning users"""
        try:
            # Get or create user wallet
            if is_returning:
                user_status = self.check_user_offering_status(username)
                if not user_status['has_wallet']:
                    raise Exception("No existing wallet found. Please initiate with your seed.")
                user_seed = user_status['stored_seed']
            
            user_wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(user_seed)
            
            # Store wallet for new users
            if not is_returning:
                self.store_user_wallet(username, user_seed)
            
            offering_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=offering_statement, 
                memo_format=username,
                memo_type='AC_OFFERING_REQUEST_RETRY' if is_returning else 'AC_OFFERING_REQUEST'
            )
            
            self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                destination_address=self.ACN_WALLET_ADDRESS,
                memo=offering_memo
            )
            
            # Generate appropriate AI response
            ai_response = self.generate_ac_character_response(
                context="OFFERING_REQUEST_RETRY" if is_returning else "OFFERING_REQUEST",
                offering_statement=offering_statement,
                username=username
            )
            
            return ai_response
            
        except Exception as e:
            error_msg = f"Error processing offering request: {str(e)}"
            print(error_msg)
            return f"The Church's mechanisms falter: {error_msg}"

    def store_user_wallet(self, username, seed):
        """Store user wallet details in database"""
        try:
            wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(seed)
            conn = self.db_connection_manager.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO acn_user_wallets (username, wallet_address, wallet_seed)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (username) DO UPDATE 
                    SET wallet_address = EXCLUDED.wallet_address,
                        wallet_seed = EXCLUDED.wallet_seed;
                """, (username, wallet.classic_address, seed))
                
                conn.commit()
                print(f"Wallet stored/updated for {username}")
                return wallet
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            raise Exception(f"Failed to store wallet: {str(e)}")

    def get_user_wallet(self, username):
        """Retrieve user wallet from database"""
        try:
            conn = self.db_connection_manager.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()
            
            try:
                cursor.execute("SELECT wallet_seed FROM acn_user_wallets WHERE username = %s", (username,))
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError(f"No wallet found for user {username}")
                
                seed = result[0]
                return self.generic_acn_utilities.spawn_user_wallet_from_seed(seed)
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            raise Exception(f"Failed to retrieve wallet: {str(e)}")

    def process_ac_offering_request(self, user_seed, offering_statement, username):
        """Handles initial offering request."""
        try:
            print("\nProcessing initial offering request...")
            user_wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(user_seed)
            
            # Store wallet for future use
            self.store_user_wallet(username, user_seed)
            
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

    def process_ac_offering_transaction(self, username, offering_amount):
        """Handles the actual PFT offering using stored wallet."""
        try:
            print("\nProcessing main offering transaction...")
            user_wallet = self.get_user_wallet(username)
            
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
        """Generates character response using LLM interface with context-based prompts."""
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
    """Test function to run real mainnet transactions"""
    try:
        print("\n=== Starting Live Blockchain Test ===")
        
        # Initialize ACNode
        node = ACNode()
        
        # First time only - need seed to store wallet
        test_wallet_seed = input("Enter your test wallet seed: ")
        test_username = "test_pilgrim"
        
        # Test initial offering request (1 PFT) - this will also store the wallet
        print("\nTesting initial offering request...")
        offering_statement = "I humbly seek the wisdom of Accelerando."
        response = node.process_ac_offering_request(
            user_seed=test_wallet_seed,  # Only needed first time
            offering_statement=offering_statement,
            username=test_username
        )
        print("\nOffering Request Response:", response)
        
        proceed = input("\nInitial request successful. Proceed with main offering? (y/n): ")
        if proceed.lower() == 'y':
            # Future transactions just need username
            print("\nTesting offering transaction...")
            offering_amount = 2  # Small test amount
            response = node.process_ac_offering_transaction(
                username=test_username,  # No seed needed, using stored wallet
                offering_amount=offering_amount
            )
            print("\nOffering Transaction Response:", response)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    live_blockchain_test()