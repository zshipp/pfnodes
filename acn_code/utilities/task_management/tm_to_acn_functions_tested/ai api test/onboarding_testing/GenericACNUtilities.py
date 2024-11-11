import xrpl
import binascii
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment, Memo
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.utils import xrp_to_drops
import json
import datetime
import nest_asyncio
nest_asyncio.apply()

class GenericACNUtilities:
    def __init__(self, pw_map, node_name='accelerandochurch'):
        self.pw_map = pw_map
        self.pft_issuer = 'rnQUEEg8yyjrwk9FhyXpKavHyCRJM9BDMW'
        self.mainnet_url = "https://xrplcluster.com"  # Keeping your existing URL
        self.node_name = node_name
        self.node_address = "rpb7dex8DMLRXunDcTbbQeteCCYcyo9uSd"
        self.node_seed = self.pw_map['acn_node__v1xrpsecret']
        
        # Initialize client with error handling
        try:
            self.client = JsonRpcClient(self.mainnet_url)
            # Test connection - this should now work with nest_asyncio
            self.client.request(xrpl.models.requests.ServerInfo())
            print(f"Connected to XRPL mainnet at {self.mainnet_url}")
        except Exception as e:
            raise Exception(f"Failed to initialize XRPL client: {str(e)}")
            
        # Initialize node wallet with error handling
        try:
            self.node_wallet = self.spawn_user_wallet_from_seed(self.node_seed)
            print(f"Initialized {node_name} node wallet: {self.node_wallet.classic_address}")
        except Exception as e:
            raise Exception(f"Failed to initialize node wallet: {str(e)}")
                
        # Verify PFT trust line exists
        try:
            if self._verify_trust_line():
                print("PFT trust line verified")
            else:
                print("Warning: No PFT trust line found for node wallet")
        except Exception as e:
            print(f"Trust line verification failed: {str(e)}")


    def _verify_trust_line(self):
        """Verify PFT trust line exists for node wallet"""
        try:
            return self.validate_pft_balance(self.node_wallet.classic_address, 0)
        except Exception as e:
            print(f"Trust line verification failed: {str(e)}")
            return False

    def validate_pft_balance(self, address, minimum_balance):
        """Validates if an address has sufficient PFT balance"""
        try:
            print(f"\nChecking PFT balance for {address}")
            response = self.client.request(xrpl.models.requests.AccountLines(
                account=address,
                ledger_index="validated"
            ))
            
            for line in response.result.get("lines", []):
                if line.get("currency") == "PFT" and line.get("account") == self.pft_issuer:
                    balance = float(line.get("balance", 0))
                    print(f"Current PFT balance: {balance}")
                    if balance >= minimum_balance:
                        print("Balance sufficient")
                        return True
                    else:
                        print(f"Insufficient balance: {balance} < {minimum_balance}")
                        return False
                        
            print("No PFT trust line found")
            return False
            
        except Exception as e:
            print(f"Balance check failed: {str(e)}")
            return False

    def log_transaction(self, tx_type, from_address, amount, result):
        """Log transaction details"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n=== Transaction Log {timestamp} ===")
        print(f"Type: {tx_type}")
        print(f"From: {from_address}")
        print(f"Amount: {amount} PFT")
        print(f"Result: {'SUCCESS' if result else 'FAILED'}")
        if isinstance(result, dict):
            print(f"Hash: {result.get('hash', 'N/A')}")
        print("================================\n")

    def send_PFT_with_info(self, sending_wallet, amount, memo, destination_address):
        """Sends PFT tokens with memo information"""
        try:
            print(f"\nInitiating transaction of {amount} PFT")
            print(f"From: {sending_wallet.classic_address}")
            print(f"To: {destination_address}")

            # Verify PFT balance before sending
            if not self.validate_pft_balance(sending_wallet.classic_address, amount):
                raise Exception(f"Insufficient PFT balance for sending {amount} PFT")

            # Create payment
            amount_to_send = IssuedCurrencyAmount(
                currency="PFT",
                issuer=self.pft_issuer,
                value=str(amount)
            )
            
            payment = Payment(
                account=sending_wallet.classic_address,
                amount=amount_to_send,
                destination=destination_address,
                memos=[memo]
            )

            # Submit and wait
            print("Submitting transaction...")
            response = xrpl.transaction.submit_and_wait(
                payment, 
                self.client, 
                sending_wallet,
                check_fee=True
            )
            
            result = response.result
            success = result.get("validated", False)
            
            # Log transaction
            self.log_transaction(
                "PFT Transfer",
                sending_wallet.classic_address,
                amount,
                result if success else None
            )

            if success:
                print(f"Transaction successful: {result['hash']}")
                return response
            else:
                raise Exception(f"Transaction failed: {result}")

        except Exception as e:
            error_msg = f"Transaction failed: {str(e)}"
            print(f"\nERROR: {error_msg}")
            raise Exception(error_msg)

    def construct_standardized_xrpl_memo(self, memo_data, memo_type, memo_format):
        """Constructs a standardized XRPL memo"""
        try:
            memo_hex = binascii.hexlify(memo_data.encode()).decode()
            memo_type_hex = binascii.hexlify(memo_type.encode()).decode()
            memo_format_hex = binascii.hexlify(memo_format.encode()).decode()
            
            memo = Memo(
                memo_data=memo_hex,
                memo_type=memo_type_hex,
                memo_format=memo_format_hex
            )
            return memo
        except Exception as e:
            raise Exception(f"Failed to construct memo: {str(e)}")

    def spawn_user_wallet_from_seed(self, seed):
        """Creates user wallet from seed"""
        try:
            wallet = Wallet.from_seed(seed)
            print(f'Wallet initialized with classic address {wallet.classic_address}')
            return wallet
        except Exception as e:
            raise Exception(f"Failed to create wallet: {str(e)}")

    def to_hex(self, string):
        """Convert string to hex"""
        return binascii.hexlify(string.encode()).decode()