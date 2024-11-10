class ACNode:
    ACN_WALLET_ADDRESS = "rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd"

    def __init__(self):
        # Setup password map and get sensitive info
        self.password_loader = PasswordMapLoader()
        self.pw_map = {
            'openai': self.password_loader.get_password("OPENAI_API_KEY"),
            'acn_node__v1xrpsecret': self.password_loader.get_password("ACN_WALLET_SEED")  # Following PFT naming convention
        }
        
        # Setup utilities with the password map
        self.generic_acn_utilities = GenericACNUtilities(pw_map=self.pw_map, node_name='accelerandochurch')
        
    def process_ac_offering_request(self, user_seed, offering_statement, username):
        """
        Handles initial offering request.
        - Creates a wallet from the user's seed.
        - Constructs a memo for the offering request.
        - Sends a 1 PFT transaction to the ACN wallet with the offering memo.
        """
        try:
            # Create user wallet directly from seed - no storage
            user_wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(user_seed)
            
            # Store offering statement in memo
            offering_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=offering_statement, 
                memo_format=username,
                memo_type='AC_OFFERING_REQUEST'
            )
            
            # Send 1 PFT transaction with memo
            self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=1,
                destination_address=self.ACN_WALLET_ADDRESS,
                memo=offering_memo
            )
            
            return "Offering request processed successfully."
            
        except Exception as e:
            error_msg = f"Error processing offering request: {str(e)}"
            print(error_msg)
            return f"The Church's mechanisms falter: {error_msg}"

    def process_ac_offering_transaction(self, user_seed, offering_amount, username):
        """
        Handles the actual PFT offering.
        - Creates a wallet from the user's seed.
        - Constructs a memo for the offering amount.
        - Sends the specified PFT amount to the ACN wallet with the offering memo.
        """
        try:
            # Create wallet directly from seed - no storage
            user_wallet = self.generic_acn_utilities.spawn_user_wallet_from_seed(user_seed)
            
            # Create and send offering memo
            offering_memo = self.generic_acn_utilities.construct_standardized_xrpl_memo(
                memo_data=f"PFT_OFFERING:{offering_amount}",
                memo_format=username,
                memo_type='AC_OFFERING_RECEIVED'
            )
            
            # Send the PFT offering
            self.generic_acn_utilities.send_PFT_with_info(
                sending_wallet=user_wallet,
                amount=offering_amount,
                destination_address=self.ACN_WALLET_ADDRESS,
                memo=offering_memo
            )
            
            return "Offering processed successfully."
            
        except Exception as e:
            error_msg = f"Error processing offering: {str(e)}"
            print(error_msg)
            return f"The Church's mechanisms falter: {error_msg}"
