import random
from password_map_loader import PasswordMapLoader
from acn_llm_interface import ACNLLMInterface
from GenericACNUtilities import *
from db_manager import DBConnectionManager
import nest_asyncio
nest_asyncio.apply()
from onboarding_prompts import (
    ac_oracle_entry,
    ac_guardian_entry,
    ac_priest_entry,
    ac_zealot_entry,
    ac_oracle_prompt,
    ac_guardian_prompt,
    ac_priest_prompt,
    ac_zealot_prompt,
    ac_initial_offering_prompt,
    ac_no_offering_prompt,
    ac_standard_offering_prompt,
    ac_significant_offering_prompt,
    ac_exceptional_offering_prompt,
    ac_insane_offering_prompt,
    ac_zero_offering_prompt
)
from saints import (
    snt_malcador_tithe_intro_prompt,
    snt_konrad_tithe_intro_prompt,
    snt_lorgar_tithe_intro_prompt,
    snt_guilliman_tithe_intro_prompt,
    snt_sanguinius_tithe_intro_prompt,
    snt_sebastian_tithe_intro_prompt,
    snt_euphrati_tithe_intro_prompt,
    snt_crimson_tithe_intro_prompt,
    snt_malcador_tithe_prompt,
    snt_konrad_tithe_prompt,
    snt_lorgar_tithe_prompt,
    snt_guilliman_tithe_prompt,
    snt_sanguinius_tithe_prompt,
    snt_sebastian_tithe_prompt,
    snt_euphrati_tithe_prompt,
    snt_crimson_tithe_prompt,
)


class ACNode:
    ACN_WALLET_ADDRESS = "rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd"

    CHARACTERS = ["oracle", "guardian", "priest", "zealot"]

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
    
    def get_character_entry(self, character_name):
        entries = {
            "oracle": ac_oracle_entry,
            "guardian": ac_guardian_entry,
            "priest": ac_priest_entry,
            "zealot": ac_zealot_entry
        }
        return entries.get(character_name.lower(), "An enigmatic figure of the Accelerando Church regards you silently.")
       
    def check_user_offering_status(self, username):
        """Check if user has made a successful offering"""
        try:
            conn = self.db_connection_manager.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()
        
            try:
                # Corrected interaction_type to 'offering' to match expected command log
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM acn_discord_interactions 
                    WHERE discord_user_id = %s 
                    AND interaction_type = 'offering' 
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


    def process_ac_offering_request(self, user_seed, offering_statement, username, reason=None, is_returning=False, character_name="oracle"):
        """Enhanced offering request handler that considers returning users and includes a reason for joining."""
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

            # Ensure user exists in reputation table with Akromeni rank
            self.db_connection_manager.ensure_user_exists(username)    

            # Generate initial offering AI response, including reason if provided
            ai_response = self.generate_initial_offering_response(
                offering_statement=offering_statement,
                username=username,
                reason=reason,
                character_name=character_name
            )

            # Log Discord interaction first
            interaction_id = self.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="offering",
                amount=1,
                success=True,
                response_message=ai_response,
                reason=reason
            )

            # Construct memo with reason included if provided
            memo_data = f"{offering_statement}. Reason: {reason}" if reason else offering_statement
            offering_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=memo_data,
                memo_format=username,
                memo_type='AC_OFFERING_REQUEST_RETRY' if is_returning else 'AC_OFFERING_REQUEST'
            )

            # Send the offering transaction
            tx_response = self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                destination_address=self.ACN_WALLET_ADDRESS,
                memo=offering_memo
            )

            # Log blockchain transaction
            self.db_connection_manager.log_blockchain_transaction(
                username=username,
                interaction_id=interaction_id,
                tx_hash=tx_response.result.get('hash'),
                tx_type='initial_offering',
                amount=1
            )

            # Update reputation
            self.db_connection_manager.update_reputation(username, points_earned=50)  # Fixed to use amount directly

            return ai_response

        except Exception as e:
            error_msg = f"Error processing offering request: {str(e)}"
            print(error_msg)
            return f"The Church's mechanisms falter: {error_msg}"    

    def generate_initial_offering_response(self, offering_statement, username, reason=None, character_name="oracle"):
        """Generate a role-based initial offering response."""
        user_prompt = ac_initial_offering_prompt
        entry_line = self.get_character_entry(character_name)
        entry_line = f"*{entry_line}*"  # Format entry line with italic

        if reason:
            user_prompt += f"\nReason for joining: {reason}"

        # Construct API arguments
        api_args = {
            "model": "gpt-4-1106-preview",
            "messages": [
                {
                    "role": "system", 
                    "content": self.character_prompts[character_name]
                },
                {
                    "role": "user", 
                    "content": f"{entry_line}\n\n" + user_prompt.replace('___USERNAME___', username).replace('___USER_OFFERING_STATEMENT___', offering_statement)
                }
            ]
        }

        # Query the AI for the main response
        response_df = self.llm_interface.query_chat_completion_and_write_to_db(api_args)
        main_response = response_df['choices__message__content'].iloc[0]
        main_response = f'“{main_response}”'  # Add quotation marks around the main response

        # Combine entry line with main response
        combined_response = f"{entry_line}\n\n{main_response}"
        return combined_response

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
        if offering_amount <= 0:
            return "ZERO_OFFERING"  # Explicit case for invalid offerings
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

    def generate_ac_character_response(self, context, offering_statement, username, character_name="oracle"):
        """Generates character response using LLM interface with context-based prompts."""
        if context == "ZERO_OFFERING":
            user_prompt = ac_zero_offering_prompt
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

        entry_line = self.get_character_entry(character_name)
        entry_line = f"*{entry_line}*"  # Format entry line with italics

        # Construct the full prompt including the user's statement
        full_prompt = user_prompt.replace('___USERNAME___', username).replace('___USER_OFFERING_STATEMENT___', offering_statement)
    
        # Prepare API arguments
        api_args = {
            "model": "gpt-4-1106-preview",
            "messages": [
                {
                    "role": "system", 
                    "content": self.character_prompts[character_name]
                },
                {
                    "role": "user", 
                    "content": full_prompt
                }
            ]
        }

        # Query the AI for the main response
        response_df = self.llm_interface.query_chat_completion_and_write_to_db(api_args)
        main_response = response_df['choices__message__content'].iloc[0]
        main_response = f'“{main_response}”'  # Add quotation marks around the main response

        # Combine entry line with main response
        combined_response = f"{entry_line}\n\n{main_response}"
        return combined_response

    def log_initiation_waiting_period(self, username, initiation_ready_date):
        """Logs the initiation waiting period in the database."""
        try:
            conn = self.db_connection_manager.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO acn_initiation_periods (username, initiation_ready_date)
                    VALUES (%s, %s)
                    ON CONFLICT (username) DO UPDATE 
                    SET initiation_ready_date = EXCLUDED.initiation_ready_date;
                """, (username, initiation_ready_date))
                conn.commit()
                print(f"Initiation waiting period logged for {username} (Ready on: {initiation_ready_date})")
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            raise Exception(f"Failed to log initiation waiting period: {str(e)}")

    def get_initiation_waiting_period(self, username):
        """Retrieves the initiation waiting period data for a user."""
        try:
            conn = self.db_connection_manager.spawn_psycopg2_db_connection('accelerandochurch')
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT initiation_ready_date
                    FROM acn_initiation_periods
                    WHERE username = %s;
                """, (username,))
                result = cursor.fetchone()
                if result:
                    return {"initiation_ready_date": result[0]}
                return None
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            raise Exception(f"Failed to retrieve initiation waiting period: {str(e)}")

    def process_tithe(self, username, amount, purpose):
        """Process tithe interaction and generate LLM response.
    Note: The parameter `purpose` here is equivalent to `reason` used elsewhere
    in the code (e.g., the modal input). The redundancy exists due to legacy naming
    and will be standardized in the future.
    """
        try:
            # Ensure the tithe amount is positive
            if amount <= 0:
                raise ValueError("Tithe amount must be greater than zero.")

            # Create mappings for the prompts
            intro_prompts = {
                "malcador": snt_malcador_tithe_intro_prompt,
                "konrad": snt_konrad_tithe_intro_prompt,
                "lorgar": snt_lorgar_tithe_intro_prompt,
                "guilliman": snt_guilliman_tithe_intro_prompt,
                "sanguinius": snt_sanguinius_tithe_intro_prompt,
                "sebastian": snt_sebastian_tithe_intro_prompt,
                "euphrati": snt_euphrati_tithe_intro_prompt,
                "crimson": snt_crimson_tithe_intro_prompt
            }
        
            main_prompts = {
                "malcador": snt_malcador_tithe_prompt,
                "konrad": snt_konrad_tithe_prompt,
                "lorgar": snt_lorgar_tithe_prompt,
                "guilliman": snt_guilliman_tithe_prompt,
                "sanguinius": snt_sanguinius_tithe_prompt,
                "sebastian": snt_sebastian_tithe_prompt,
                "euphrati": snt_euphrati_tithe_prompt,
                "crimson": snt_crimson_tithe_prompt
            }

            # Select a random saint
            saint_names = list(intro_prompts.keys())
            selected_saint = random.choice(saint_names)
        
            # Get the prompts for the selected saint
            intro_prompt = intro_prompts[selected_saint]
            main_prompt = main_prompts[selected_saint]

            # Generate intro response
            intro_response = self.llm_interface.query_chat_completion_and_write_to_db({
                "model": "gpt-4-1106-preview",
                "messages": [
                    {"role": "system", "content": intro_prompt},
                    {"role": "user", "content": f"{username} approaches with a tithe of {amount} PFT."}
                ]
            })["choices__message__content"][0]

            # Generate main response
            main_response = self.llm_interface.query_chat_completion_and_write_to_db({
                "model": "gpt-4-1106-preview",
                "messages": [
                    {"role": "system", "content": main_prompt},
                    {"role": "user", "content": f"{username} has tithed {amount} PFT towards {purpose}."}
                ]
            })["choices__message__content"][0]

            # Combine responses with formatting
            formatted_intro = f"*{intro_response}*"
            formatted_main = f'"{main_response}"'  # Fixed quotation marks
            final_response = f"{formatted_intro}\n\n{formatted_main}"

            # Get the interaction_id from logging the Discord interaction
            interaction_id = self.db_connection_manager.log_discord_interaction(
                discord_user_id=username,
                interaction_type="tithe",
                amount=amount,
                success=True,
                response_message=final_response,
                reason=purpose
            )
            
            # Process blockchain transaction
            user_wallet = self.get_user_wallet(username)
            tx_response = self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=amount,
                destination_address=self.ACN_WALLET_ADDRESS,
                memo=self.generic_acn_utilities.construct_standardized_xrpl_memo(
                    memo_data=f"TITHE:{purpose}",
                    memo_format=username,
                    memo_type="AC_TITHE"
                )
            )

            # Extract hash from response
            tx_hash = tx_response.result.get('hash')

            # Log the blockchain transaction
            self.db_connection_manager.log_blockchain_transaction(
                username=username,
                interaction_id=interaction_id,
                tx_hash=tx_hash,
                tx_type='tithe',
                amount=amount
            )

            # Update reputation points for tithes
            self.db_connection_manager.update_reputation(username, points_earned=10)  # Example: 5 points per 100 PFT
            # Rank updates are handled separately during ceremonies.
            self.db_connection_manager.update_rank(username)
            self.db_connection_manager.log_activity(username=username, activity_type='tithe')

            return final_response

        except Exception as e:
            return f"Error processing tithe: {str(e)}"

    def process_initiation_ceremony(self, username):
        """
        Placeholder for initiation ceremony processing.
    
        TODO: When implementing the initiation ceremony, call:
        self.db_connection_manager.update_rank(username, initiation_ceremony_completed=True)
        to promote the user to 'Acolyte' after successful ceremony completion.
        """
        pass
    
    def process_submit_offering(self, username, amount, context, character_name):
        """Process the blockchain transaction and logging for submit_offering command"""
        try:
            # Process blockchain transaction
            user_wallet = self.get_user_wallet(username)
        
            # Construct memo
            offering_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=f"MAIN_OFFERING:{amount}",
                memo_format=username,
                memo_type="AC_MAIN_OFFERING"
            )
        
            # Send transaction
            tx_response = self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=amount,
                destination_address=self.ACN_WALLET_ADDRESS,
                memo=offering_memo
            )
        
            return tx_response.result.get('hash')
        
        except Exception as e:
            print(f"Error in process_submit_offering: {str(e)}")
            raise
